import {createHash, createPublicKey, verify as verifySignature, randomUUID} from 'node:crypto';
import {lstat, mkdir, readFile, readdir, rename, rm, copyFile, writeFile} from 'node:fs/promises';
import {join, resolve, relative, sep, posix} from 'node:path';

const SCHEMA = 'sovereign.release.v1';
const MAX_FILES = 10000;
const MAX_FILE_BYTES = 128 * 1024 * 1024;
const MAX_TOTAL_BYTES = 512 * 1024 * 1024;

function fail(code) { throw new Error(code); }
function safeRelativePath(value) {
  if (typeof value !== 'string' || !value || value.includes('\\\\') || value.startsWith('/') || value.includes('\\0')) return false;
  const normalized = posix.normalize(value);
  return normalized === value && normalized !== '.' && normalized !== '..' && !normalized.startsWith('../') && !value.split('/').some(part => !part || part === '.' || part === '..');
}
function inside(root, candidate) {
  const rel = relative(root, candidate);
  return rel === '' || (rel !== '..' && !rel.startsWith('..' + sep) && !resolve(rel).startsWith(sep));
}
async function regularFile(root, relativePath) {
  if (!safeRelativePath(relativePath)) fail('unsafe_release_path');
  const full = resolve(root, ...relativePath.split('/'));
  if (!inside(root, full)) fail('unsafe_release_path');
  const stat = await lstat(full);
  if (!stat.isFile() || stat.isSymbolicLink()) fail('release_file_must_be_regular');
  if (stat.size > MAX_FILE_BYTES) fail('release_file_too_large');
  return {full, stat};
}
async function atomicJson(path, value) {
  await mkdir(resolve(path, '..'), {recursive:true});
  const temp = path + '.' + randomUUID() + '.tmp';
  await writeFile(temp, JSON.stringify(value, null, 2) + '\n', {mode:0o600, flag:'wx'});
  await rename(temp, path);
}
export async function verifyRelease(directory, {publicKey = process.env.SOVEREIGN_RELEASE_PUBLIC_KEY, allowUnsignedLocal = false} = {}) {
  const root = resolve(directory);
  const manifestPath = join(root, 'release.json');
  const manifestBytes = await readFile(manifestPath);
  let manifest;
  try { manifest = JSON.parse(manifestBytes.toString('utf8')); } catch { fail('invalid_release_manifest'); }
  if (!manifest || manifest.schema !== SCHEMA || !/^[a-z0-9][a-z0-9._-]{0,79}$/.test(manifest.releaseId || '')) fail('invalid_release_manifest');
  if (!Array.isArray(manifest.files) || manifest.files.length < 1 || manifest.files.length > MAX_FILES) fail('invalid_release_file_list');
  if (typeof manifest.entrypoint !== 'string' || !safeRelativePath(manifest.entrypoint)) fail('invalid_release_entrypoint');
  const seen = new Set();
  let total = 0;
  for (const item of manifest.files) {
    if (!item || !safeRelativePath(item.path) || seen.has(item.path) || !/^[a-f0-9]{64}$/.test(item.sha256 || '') || !Number.isSafeInteger(item.size) || item.size < 0) fail('invalid_release_file_entry');
    seen.add(item.path);
    const {full, stat} = await regularFile(root, item.path);
    if (stat.size !== item.size) fail('release_file_size_mismatch:' + item.path);
    total += stat.size;
    if (total > MAX_TOTAL_BYTES) fail('release_total_size_exceeded');
    const digest = createHash('sha256').update(await readFile(full)).digest('hex');
    if (digest !== item.sha256) fail('release_file_hash_mismatch:' + item.path);
  }
  if (!seen.has(manifest.entrypoint)) fail('release_entrypoint_not_listed');
  let signed = false;
  try {
    const signature = (await readFile(join(root, 'manifest.sig'), 'utf8')).trim();
    if (!publicKey || !signature) fail('release_signature_key_missing');
    const key = createPublicKey(publicKey);
    signed = verifySignature(null, manifestBytes, key, Buffer.from(signature, 'base64'));
    if (!signed) fail('release_signature_invalid');
  } catch (error) {
    if (error.message === 'release_signature_key_missing' || error.message === 'release_signature_invalid') throw error;
    if (!allowUnsignedLocal || error.code !== 'ENOENT') throw error;
  }
  if (!signed && !allowUnsignedLocal) fail('unsigned_release_not_allowed');
  return {manifest, signed, totalBytes:total, fileCount:manifest.files.length};
}
export async function installRelease(sourceDirectory, stateDirectory, options = {}) {
  const checked = await verifyRelease(sourceDirectory, options);
  const root = resolve(stateDirectory), releases = join(root, 'releases');
  await mkdir(releases, {recursive:true});
  const destination = join(releases, checked.manifest.releaseId);
  try { await lstat(destination); fail('release_already_installed'); } catch (error) { if (error.code !== 'ENOENT') throw error; }
  const staging = join(releases, '.staging-' + randomUUID());
  await mkdir(staging, {recursive:false});
  try {
    for (const item of checked.manifest.files) {
      const {full} = await regularFile(resolve(sourceDirectory), item.path);
      const target = join(staging, ...item.path.split('/'));
      await mkdir(resolve(target, '..'), {recursive:true});
      await copyFile(full, target);
    }
    await copyFile(join(resolve(sourceDirectory), 'release.json'), join(staging, 'release.json'));
    if (checked.signed) await copyFile(join(resolve(sourceDirectory), 'manifest.sig'), join(staging, 'manifest.sig'));
    await verifyRelease(staging, options);
    await rename(staging, destination);
    const statePath = join(root, 'state.json');
    let previous = null;
    try { previous = JSON.parse(await readFile(statePath, 'utf8')).active || null; } catch (error) { if (error.code !== 'ENOENT') throw error; }
    await atomicJson(statePath, {schema:'sovereign.deploy-state.v1', active:checked.manifest.releaseId, previous, updatedAt:new Date().toISOString()});
    return {releaseId:checked.manifest.releaseId, previous, signed:checked.signed, statePath};
  } catch (error) {
    await rm(staging, {recursive:true, force:true});
    throw error;
  }
}
export async function rollback(stateDirectory) {
  const root = resolve(stateDirectory), statePath = join(root, 'state.json');
  const state = JSON.parse(await readFile(statePath, 'utf8'));
  if (state.schema !== 'sovereign.deploy-state.v1' || !state.previous) fail('no_previous_release');
  await lstat(join(root, 'releases', state.previous, 'release.json'));
  await atomicJson(statePath, {schema:state.schema, active:state.previous, previous:state.active, updatedAt:new Date().toISOString()});
  return {active:state.previous, previous:state.active};
}
export async function readDeploymentStatus(stateDirectory) {
  const root = resolve(stateDirectory);
  try {
    const state = JSON.parse(await readFile(join(root, 'state.json'), 'utf8'));
    if (state.schema !== 'sovereign.deploy-state.v1') fail('invalid_deploy_state');
    return state;
  } catch (error) { if (error.code === 'ENOENT') return {schema:'sovereign.deploy-state.v1',active:null,previous:null}; throw error; }
}
