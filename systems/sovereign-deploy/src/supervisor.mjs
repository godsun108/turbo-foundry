import http from 'node:http';
import {spawn} from 'node:child_process';
import {join} from 'node:path';
import {readDeploymentStatus, verifyRelease, rollback} from './release.mjs';

const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
function safeHealthPath(value){return typeof value==='string'&&/^\\/[A-Za-z0-9/_-]*$/.test(value)&&!value.startsWith('//')}

async function freePort(){
  const server=http.createServer();
  await new Promise((resolve,reject)=>server.once('error',reject).listen(0,'127.0.0.1',resolve));
  const port=server.address().port;
  await new Promise(resolve=>server.close(resolve));
  return port;
}
async function waitHealthy(child,port,path,timeoutMs){
  const deadline=Date.now()+timeoutMs;
  while(Date.now()<deadline){
    if(child.exitCode!==null||child.signalCode!==null)throw new Error('release_process_exited_before_healthcheck');
    try{
      const response=await fetch('http://127.0.0.1:'+port+path,{signal:AbortSignal.timeout(900)});
      if(response.ok)return;
    }catch{}
    await sleep(200);
  }
  throw new Error('release_healthcheck_timeout');
}
export async function startSupervisor({stateDirectory,port=8080,host='0.0.0.0',publicKey=process.env.SOVEREIGN_RELEASE_PUBLIC_KEY,allowUnsignedLocal=process.env.SOVEREIGN_ALLOW_UNSIGNED_LOCAL==='1',healthPath=process.env.SOVEREIGN_HEALTH_PATH||'/health',startupTimeoutMs=15000,pollMs=500,drainMs=1500}={}){
  if(!stateDirectory)throw new Error('state_directory_required');
  if(!safeHealthPath(healthPath))throw new Error('invalid_supervisor_health_path');
  let active=null,activeReleaseId=null,lastFailedReleaseId=null,busy=false,closed=false;
  const children=new Set();
  const server=http.createServer((req,res)=>{
    if(!active){res.writeHead(503,{'content-type':'application/json','cache-control':'no-store'});res.end(JSON.stringify({error:'no_healthy_release'}));return}
    const upstream=http.request({hostname:'127.0.0.1',port:active.port,path:req.url,method:req.method,headers:{...req.headers,host:'127.0.0.1:'+active.port}},upstreamRes=>{
      res.writeHead(upstreamRes.statusCode||502,upstreamRes.headers);upstreamRes.pipe(res);
    });
    upstream.on('error',()=>{if(!res.headersSent){res.writeHead(502,{'content-type':'application/json'});res.end(JSON.stringify({error:'upstream_unavailable'}))}else res.destroy()});
    req.pipe(upstream);
  });
  async function sync(){
    if(busy||closed)return;
    busy=true;
    try{
      const state=await readDeploymentStatus(stateDirectory);
      if(!state.active||state.active===activeReleaseId||state.active===lastFailedReleaseId)return;
      const releaseDirectory=join(stateDirectory,'releases',state.active);
      const checked=await verifyRelease(releaseDirectory,{publicKey,allowUnsignedLocal});
      const selectedHealthPath=checked.manifest.healthPath||healthPath;
      if(!safeHealthPath(selectedHealthPath))throw new Error('invalid_release_health_path');
      const childPort=await freePort();
      const entrypoint=join(releaseDirectory,...checked.manifest.entrypoint.split('/'));
      const child=spawn(process.execPath,[entrypoint],{cwd:releaseDirectory,env:{...process.env,PORT:String(childPort)},stdio:'ignore'});
      children.add(child);
      try{
        await waitHealthy(child,childPort,selectedHealthPath,startupTimeoutMs);
        const previous=active;
        active={port:childPort,child,releaseId:state.active};
        activeReleaseId=state.active;lastFailedReleaseId=null;
        if(previous){
          const timer=setTimeout(()=>{previous.child.kill('SIGTERM');children.delete(previous.child)},drainMs);
          timer.unref?.();
        }
      }catch(error){
        lastFailedReleaseId=state.active;
        child.kill('SIGTERM');children.delete(child);
        if(state.previous){
          try{await rollback(stateDirectory)}catch{}
        }
        console.error('Sovereign release activation rejected:',error.message);
      }
    }catch(error){console.error('Sovereign deploy supervisor:',error.message)}
    finally{busy=false}
  }
  await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(port,host,resolve)});
  await sync();
  const poll=setInterval(()=>void sync(),pollMs);poll.unref?.();
  return {
    server,
    address:server.address(),
    async close(){
      closed=true;clearInterval(poll);
      await new Promise(resolve=>server.close(resolve));
      for(const child of children)child.kill('SIGTERM');
      children.clear();
    }
  };
}
