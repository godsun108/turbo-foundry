import {createHash, createPrivateKey, sign} from 'node:crypto';
import {lstat, readdir, mkdir, readFile, writeFile, copyFile} from 'node:fs/promises';
import {join, resolve, relative, sep, isAbsolute, posix} from 'node:path';

const MAX_FILES=10000, MAX_FILE_BYTES=128*1024*1024, MAX_TOTAL_BYTES=512*1024*1024;
function fail(code){throw new Error(code)}
function safePath(value){return typeof value==='string'&&value&&!value.includes('\\')&&!value.includes('\0')&&!value.startsWith('/')&&posix.normalize(value)===value&&!value.split('/').some(p=>!p||p==='.'||p==='..')}
function inside(root,candidate){const rel=relative(root,candidate);return rel===''||(rel!=='..'&&!rel.startsWith('..'+sep)&&!isAbsolute(rel))}
export async function packRelease(sourceDirectory,releaseId,entrypoint,privateKeyPem,outputDirectory,{healthPath='/health'}={}){
  if(!/^[a-z0-9][a-z0-9._-]{0,79}$/.test(releaseId||''))fail('invalid_release_id');
  if(!safePath(entrypoint))fail('invalid_release_entrypoint');
  if(typeof healthPath!=='string'||!/^\/[A-Za-z0-9/_-]*$/.test(healthPath)||healthPath.startsWith('//'))fail('invalid_release_health_path');
  const source=resolve(sourceDirectory),output=resolve(outputDirectory);
  const rootStat=await lstat(source);
  if(!rootStat.isDirectory()||rootStat.isSymbolicLink())fail('source_root_must_be_directory');
  if(inside(source,output))fail('output_must_be_outside_source');
  const files=[];let total=0;
  async function walk(dir,prefix=''){
    for(const item of await readdir(dir,{withFileTypes:true})){
      if(!prefix&&(item.name==='release.json'||item.name==='manifest.sig'))continue;
      const rel=prefix?prefix+'/'+item.name:item.name;
      if(!safePath(rel))fail('unsafe_source_path');
      const full=join(dir,item.name),stat=await lstat(full);
      if(stat.isSymbolicLink())fail('source_symlink_not_allowed');
      if(stat.isDirectory()){await walk(full,rel);continue}
      if(!stat.isFile())fail('source_special_file_not_allowed');
      if(stat.size>MAX_FILE_BYTES)fail('release_file_too_large');
      total+=stat.size;if(total>MAX_TOTAL_BYTES)fail('release_total_size_exceeded');
      const bytes=await readFile(full);
      files.push({path:rel,sha256:createHash('sha256').update(bytes).digest('hex'),size:bytes.length,source:full});
      if(files.length>MAX_FILES)fail('release_file_count_exceeded');
    }
  }
  await walk(source);
  if(!files.length||!files.some(file=>file.path===entrypoint))fail('release_entrypoint_not_found');
  try{await lstat(output);fail('output_directory_already_exists')}catch(error){if(error.code!=='ENOENT')throw error}
  await mkdir(resolve(output,'..'),{recursive:true});
  await mkdir(output,{recursive:false});
  for(const file of files){const target=join(output,...file.path.split('/'));await mkdir(resolve(target,'..'),{recursive:true});await copyFile(file.source,target)}
  const manifest={schema:'sovereign.release.v1',releaseId,createdAt:new Date().toISOString(),entrypoint,healthPath,files:files.map(({path,sha256,size})=>({path,sha256,size}))};
  const bytes=Buffer.from(JSON.stringify(manifest));
  const signature=sign(null,bytes,createPrivateKey(privateKeyPem)).toString('base64');
  await writeFile(join(output,'release.json'),bytes,{flag:'wx',mode:0o600});
  await writeFile(join(output,'manifest.sig'),signature+'\n',{flag:'wx',mode:0o600});
  return {manifest,outputDirectory:output,totalBytes:total};
}
if(import.meta.url===new URL(process.argv[1],'file:').href){
  const [source,id,entrypoint,keyFile,output,healthPath='/health']=process.argv.slice(2);
  if(!source||!id||!entrypoint||!keyFile||!output){console.error('Usage: node src/pack.mjs <source-dir> <release-id> <entrypoint> <private-key.pem> <output-dir> [health-path]');process.exit(2)}
  try{const result=await packRelease(source,id,entrypoint,await readFile(keyFile,'utf8'),output,{healthPath});console.log(JSON.stringify({releaseId:result.manifest.releaseId,files:result.manifest.files.length,totalBytes:result.totalBytes,outputDirectory:result.outputDirectory},null,2))}
  catch(error){console.error(JSON.stringify({ok:false,error:error.message}));process.exitCode=1}
}
