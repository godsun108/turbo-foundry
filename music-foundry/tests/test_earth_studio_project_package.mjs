import test from "node:test";
import assert from "node:assert/strict";
import {webcrypto} from "node:crypto";
import {createProjectArchive,readProjectArchive} from "../earth-studio/project-package.mjs";

const encoder=new TextEncoder();
const digest=async bytes=>Array.from(new Uint8Array(await webcrypto.subtle.digest("SHA-256",bytes)),b=>b.toString(16).padStart(2,"0")).join("");
async function fixture(){
  const bytes=encoder.encode("earth-studio-original-audio");
  const blob=new Blob([bytes],{type:"audio/wav"});
  const session={
    format:"earthsession",schemaVersion:1,id:"project-1",name:"Portable Test",
    createdAt:"2026-11-24T12:00:00.000Z",updatedAt:"2026-11-24T12:00:00.000Z",
    tempo:124,meter:{numerator:4,denominator:4},sampleRate:48000,
    tracks:[{id:"track-1",name:"Audio",kind:"audio",gain:1,pan:0,muted:false,solo:false,
      clips:[{id:"clip-1",assetId:"asset-1",startSeconds:1,sourceStartSeconds:0,durationSeconds:2}]}],
    assets:[{id:"asset-1",storageKey:"audio/asset-1.wav",mediaType:"audio/wav",sizeBytes:bytes.length,sha256:await digest(bytes)}]
  };
  return {session,assets:[{id:"asset-1",blob}]};
}
test("portable archive round-trips manifest and original audio bytes",async()=>{
  const {session,assets}=await fixture();
  const archive=await createProjectArchive(session,assets,webcrypto);
  assert.equal(archive.type,"application/zip");
  const restored=await readProjectArchive(archive,webcrypto);
  assert.deepEqual(restored.session,session);
  assert.deepEqual(new Uint8Array(await restored.assets[0].blob.arrayBuffer()),new Uint8Array(await assets[0].blob.arrayBuffer()));
});
test("rejects an audio asset whose SHA-256 does not match the manifest",async()=>{
  const {session,assets}=await fixture();
  const wrong=new Blob(["different audio"],{type:"audio/wav"});
  await assert.rejects(()=>createProjectArchive(session,[{id:"asset-1",blob:wrong}],webcrypto),/size|SHA-256/);
});
test("rejects malformed archive bytes",async()=>{
  await assert.rejects(()=>readProjectArchive(new Uint8Array([1,2,3,4]),webcrypto),/ZIP|Package/);
});
test("rejects archive data changed after its CRC was recorded",async()=>{
  const {session,assets}=await fixture();
  const archive=new Uint8Array(await (await createProjectArchive(session,assets,webcrypto)).arrayBuffer());
  const marker=encoder.encode("earth-studio-original-audio");
  let found=-1;
  outer:for(let i=0;i<=archive.length-marker.length;i++){for(let j=0;j<marker.length;j++)if(archive[i+j]!==marker[j])continue outer;found=i;break;}
  assert.notEqual(found,-1);
  archive[found]^=1;
  await assert.rejects(()=>readProjectArchive(archive,webcrypto),/CRC/);
});
test("rejects unsafe traversal paths before reading package assets",async()=>{
  const {session,assets}=await fixture();
  const archive=new Uint8Array(await (await createProjectArchive(session,assets,webcrypto)).arrayBuffer());
  const marker=encoder.encode("assets/audio/asset-1.wav");
  let replacements=0;
  for(let i=0;i<=archive.length-marker.length;i++){
    let match=true;for(let j=0;j<marker.length;j++)if(archive[i+j]!==marker[j]){match=false;break;}
    if(match){archive[i]=46;archive[i+1]=46;archive[i+2]=47;replacements++;i+=marker.length-1;}
  }
  assert.equal(replacements,2);
  await assert.rejects(()=>readProjectArchive(archive,webcrypto),/Unsafe/);
});
test("rejects duplicate asset package paths",async()=>{
  const {session,assets}=await fixture();
  const duplicate={...session,assets:[...session.assets,{...session.assets[0],id:"asset-2"}]};
  await assert.rejects(()=>createProjectArchive(duplicate,[...assets,{id:"asset-2",blob:assets[0].blob}],webcrypto),/duplicate|Invalid EARTH STUDIO session/i);
});
test("rejects missing asset payloads",async()=>{
  const {session}=await fixture();
  await assert.rejects(()=>createProjectArchive(session,[],webcrypto),/exactly once/);
});
