import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, mkdir, writeFile, readFile, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createServer as createNetServer} from 'node:net';
import {createHash, generateKeyPairSync, sign} from 'node:crypto';
import {verifyRelease, installRelease, rollback, readDeploymentStatus} from '../src/release.mjs';
import {packRelease} from '../src/pack.mjs';
import {startSupervisor} from '../src/supervisor.mjs';

async function freePort(){
  const server=createNetServer();
  await new Promise((resolve,reject)=>server.once('error',reject).listen(0,'127.0.0.1',resolve));
  const {port}=server.address();
  await new Promise(resolve=>server.close(resolve));
  return port;
}

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

test('packs a source directory into a signed, verifiable release bundle',async t=>{
  const root=await mkdtemp(join(tmpdir(),'sovereign-pack-'));
  t.after(()=>rm(root,{recursive:true,force:true}));
  const source=join(root,'app'),output=join(root,'bundle');
  await mkdir(join(source,'assets'),{recursive:true});
  await writeFile(join(source,'server.mjs'),'export default true;\\n');
  await writeFile(join(source,'assets','style.css'),'body{}\\n');
  const {privateKey,publicKey}=generateKeyPairSync('ed25519');
  const packed=await packRelease(source,'packed-test','server.mjs',privateKey.export({type:'pkcs8',format:'pem'}),output);
  const verified=await verifyRelease(output,{publicKey:publicKey.export({type:'spki',format:'pem'})});
  assert.equal(verified.signed,true);
  assert.equal(verified.fileCount,2);
  assert.equal(packed.manifest.entrypoint,'server.mjs');
});

test('supervisor routes traffic only after a signed release passes its healthcheck',async t=>{
  const root=await mkdtemp(join(tmpdir(),'sovereign-supervisor-'));
  t.after(()=>rm(root,{recursive:true,force:true}));
  const source=join(root,'app'),bundle=join(root,'bundle'),state=join(root,'state');
  await mkdir(source);
  await writeFile(join(source,'server.mjs'),"import http from 'node:http';const s=http.createServer((q,r)=>{r.writeHead(q.url==='/health'?200:404);r.end('healthy-v1')});s.listen(Number(process.env.PORT),'0.0.0.0');");
  const {privateKey,publicKey}=generateKeyPairSync('ed25519');
  const privatePem=privateKey.export({type:'pkcs8',format:'pem'}),publicPem=publicKey.export({type:'spki',format:'pem'});
  await packRelease(source,'runtime-v1','server.mjs',privatePem,bundle);
  await installRelease(bundle,state,{publicKey:publicPem});
  const port=await freePort();
  const runtime=await startSupervisor({stateDirectory:state,port,host:'127.0.0.1',publicKey:publicPem,pollMs:100,startupTimeoutMs:4000});
  t.after(()=>runtime.close());
  const response=await fetch('http://127.0.0.1:'+port+'/health');
  assert.equal(response.status,200);
  assert.equal(await response.text(),'healthy-v1');
});

test('failed healthcheck rolls state back and keeps the prior release serving',async t=>{
  const root=await mkdtemp(join(tmpdir(),'sovereign-rollback-'));
  t.after(()=>rm(root,{recursive:true,force:true}));
  const {privateKey,publicKey}=generateKeyPairSync('ed25519');
  const privatePem=privateKey.export({type:'pkcs8',format:'pem'}),publicPem=publicKey.export({type:'spki',format:'pem'});
  const state=join(root,'state'),port=await freePort();
  async function build(id,body){
    const source=join(root,id),bundle=join(root,id+'-bundle');await mkdir(source);
    await writeFile(join(source,'server.mjs'),body);
    await packRelease(source,id,'server.mjs',privatePem,bundle);
    return bundle;
  }
  const good=await build('good-v1',"import http from 'node:http';const s=http.createServer((q,r)=>{r.writeHead(q.url==='/health'?200:404);r.end('good')});s.listen(Number(process.env.PORT),'0.0.0.0');");
  await installRelease(good,state,{publicKey:publicPem});
  const runtime=await startSupervisor({stateDirectory:state,port,host:'127.0.0.1',publicKey:publicPem,pollMs:50,startupTimeoutMs:1000});
  t.after(()=>runtime.close());
  assert.equal(await (await fetch('http://127.0.0.1:'+port+'/health')).text(),'good');
  const bad=await build('bad-v2',"import http from 'node:http';const s=http.createServer((q,r)=>{r.writeHead(503);r.end('not-ready')});s.listen(Number(process.env.PORT),'0.0.0.0');");
  await installRelease(bad,state,{publicKey:publicPem});
  let rolledBack=false;
  for(let i=0;i<50;i++){
    const current=await readDeploymentStatus(state);
    if(current.active==='good-v1'){rolledBack=true;break}
    await new Promise(resolve=>setTimeout(resolve,50));
  }
  assert.equal(rolledBack,true,'failed release should restore the previous active pointer');
  assert.equal(await (await fetch('http://127.0.0.1:'+port+'/health')).text(),'good');
});
