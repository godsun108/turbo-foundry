import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, mkdir, writeFile, readFile, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createHash, generateKeyPairSync, sign} from 'node:crypto';
import {verifyRelease, installRelease, rollback, readDeploymentStatus} from '../src/release.mjs';

async function fixture(t, {tamper=false, unsafePath=false}={}) {
  const root = await mkdtemp(join(tmpdir(),'sovereign-release-'));
  t.after(()=>rm(root,{recursive:true,force:true}));
  const source = join(root,'source'); await mkdir(source);
  const payload = Buffer.from('export default true;\n');
  await writeFile(join(source,'server.mjs'),payload);
  const manifest = {schema:'sovereign.release.v1',releaseId:'test-'+Date.now(),createdAt:new Date().toISOString(),entrypoint:unsafePath?'../escape.mjs':'server.mjs',files:[{path:unsafePath?'../escape.mjs':'server.mjs',sha256:createHash('sha256').update(payload).digest('hex'),size:payload.length}]};
  const bytes = Buffer.from(JSON.stringify(manifest));
  await writeFile(join(source,'release.json'),bytes);
  const {privateKey,publicKey} = generateKeyPairSync('ed25519');
  await writeFile(join(source,'manifest.sig'),sign(null,bytes,privateKey).toString('base64'));
  if(tamper) await writeFile(join(source,'server.mjs'),'changed');
  return {root,source,publicKey:publicKey.export({type:'spki',format:'pem'}),releaseId:manifest.releaseId};
}

test('verifies a signed release and its file hashes',async t=>{
  const f=await fixture(t);
  const result=await verifyRelease(f.source,{publicKey:f.publicKey});
  assert.equal(result.signed,true); assert.equal(result.fileCount,1);
});
test('rejects tampered release payloads',async t=>{
  const f=await fixture(t,{tamper:true});
  await assert.rejects(()=>verifyRelease(f.source,{publicKey:f.publicKey}),/release_file_size_mismatch|release_file_hash_mismatch/);
});
test('rejects path traversal in a release manifest',async t=>{
  const f=await fixture(t,{unsafePath:true});
  await assert.rejects(()=>verifyRelease(f.source,{publicKey:f.publicKey}),/invalid_release_entrypoint|invalid_release_file_entry/);
});
test('installs atomically and can roll back to the previous release',async t=>{
  const f=await fixture(t),state=join(f.root,'state');
  const first=await installRelease(f.source,state,{publicKey:f.publicKey});
  assert.equal(first.releaseId,f.releaseId);
  const status=await readDeploymentStatus(state);
  assert.equal(status.active,f.releaseId);
  const secondSource=join(f.root,'second'); await mkdir(secondSource);
  const payload=Buffer.from('export default 2;\n');
  await writeFile(join(secondSource,'server.mjs'),payload);
  const manifest={schema:'sovereign.release.v1',releaseId:'second-'+Date.now(),createdAt:new Date().toISOString(),entrypoint:'server.mjs',files:[{path:'server.mjs',sha256:createHash('sha256').update(payload).digest('hex'),size:payload.length}]};
  const bytes=Buffer.from(JSON.stringify(manifest)); await writeFile(join(secondSource,'release.json'),bytes);
  const {privateKey}=generateKeyPairSync('ed25519'); await writeFile(join(secondSource,'manifest.sig'),sign(null,bytes,privateKey).toString('base64'));
  const publicKey=(await import('node:crypto')).createPublicKey(privateKey).export({type:'spki',format:'pem'});
  await installRelease(secondSource,state,{publicKey});
  const rolled=await rollback(state);
  assert.equal(rolled.active,f.releaseId);
  assert.equal((await readDeploymentStatus(state)).active,f.releaseId);
  assert.ok(await readFile(join(state,'releases',f.releaseId,'server.mjs')));
});
test('unsigned releases fail closed by default',async t=>{
  const f=await fixture(t); await rm(join(f.source,'manifest.sig'));
  await assert.rejects(()=>verifyRelease(f.source),/unsigned_release_not_allowed/);
});
