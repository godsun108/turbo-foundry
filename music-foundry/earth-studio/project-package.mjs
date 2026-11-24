/**
 * EARTH STUDIO portable .earthsession package.
 *
 * Dependency-free ZIP "store" (no compression) container. This keeps the
 * project manifest and original audio assets together without a server,
 * cloud account, or third-party archive dependency.
 *
 * Only UTF-8 ZIP entries using method 0 are accepted. ZIP64, encryption,
 * compression, directory entries, and paths outside the package are rejected.
 */
import {decodeSession, MAX_PROJECT_BYTES} from "./session-store.mjs";

const encoder = new TextEncoder();
const decoder = new TextDecoder("utf-8", {fatal:true});
const MAX_ENTRIES = 10002;
const MAX_ARCHIVE_BYTES = MAX_PROJECT_BYTES + 16 * 1024 * 1024;
const EOCD = 0x06054b50;
const CENTRAL = 0x02014b50;
const LOCAL = 0x04034b50;
const crcTable = new Uint32Array(256);
for (let n=0;n<256;n++) {
  let c=n;
  for (let k=0;k<8;k++) c=(c&1)?(0xedb88320^(c>>>1)):(c>>>1);
  crcTable[n]=c>>>0;
}
function crc32(bytes) {
  let crc=0xffffffff;
  for (const byte of bytes) crc=crcTable[(crc^byte)&0xff]^(crc>>>8);
  return (crc^0xffffffff)>>>0;
}
function concat(parts) {
  const size=parts.reduce((n,p)=>n+p.length,0);
  const out=new Uint8Array(size);let offset=0;
  for(const part of parts){out.set(part,offset);offset+=part.length;}
  return out;
}
function safePath(path) {
  if(typeof path!=="string"||!path||path.startsWith("/")||path.includes("\\")||path.includes("\0"))return false;
  const parts=path.split("/");
  return parts.every(part=>part&&part!=="."&&part!=="..") && (path==="manifest.json"||path.startsWith("assets/"));
}
function dosDateTime() { return {time:0,date:33}; } // 1980-01-01; stable and timezone-independent.
function makeZip(entries) {
  if(entries.length<1||entries.length>MAX_ENTRIES)throw new RangeError("Package entry count is outside the supported limit");
  const localParts=[],centralParts=[];let offset=0;
  for(const entry of entries){
    const name=encoder.encode(entry.name),data=entry.bytes;
    if(name.length>65535||data.length>0xffffffff)throw new RangeError("A package entry exceeds classic ZIP limits");
    const crc=crc32(data),stamp=dosDateTime();
    const local=new Uint8Array(30+name.length),lv=new DataView(local.buffer);
    lv.setUint32(0,LOCAL,true);lv.setUint16(4,20,true);lv.setUint16(6,0x0800,true);
    lv.setUint16(8,0,true);lv.setUint16(10,stamp.time,true);lv.setUint16(12,stamp.date,true);
    lv.setUint32(14,crc,true);lv.setUint32(18,data.length,true);lv.setUint32(22,data.length,true);
    lv.setUint16(26,name.length,true);lv.setUint16(28,0,true);local.set(name,30);
    localParts.push(local,data);
    const central=new Uint8Array(46+name.length),cv=new DataView(central.buffer);
    cv.setUint32(0,CENTRAL,true);cv.setUint16(4,20,true);cv.setUint16(6,20,true);
    cv.setUint16(8,0x0800,true);cv.setUint16(10,0,true);
    cv.setUint16(12,stamp.time,true);cv.setUint16(14,stamp.date,true);
    cv.setUint32(16,crc,true);cv.setUint32(20,data.length,true);cv.setUint32(24,data.length,true);
    cv.setUint16(28,name.length,true);cv.setUint16(30,0,true);cv.setUint16(32,0,true);
    cv.setUint16(34,0,true);cv.setUint16(36,0,true);cv.setUint32(38,0,true);
    cv.setUint32(42,offset,true);central.set(name,46);centralParts.push(central);
    offset+=local.length+data.length;
    if(offset>0xffffffff)throw new RangeError("Package exceeds classic ZIP size limits");
  }
  const centralBytes=concat(centralParts),centralOffset=offset;
  const end=new Uint8Array(22),ev=new DataView(end.buffer);
  ev.setUint32(0,EOCD,true);ev.setUint16(4,0,true);ev.setUint16(6,0,true);
  ev.setUint16(8,entries.length,true);ev.setUint16(10,entries.length,true);
  ev.setUint32(12,centralBytes.length,true);ev.setUint32(16,centralOffset,true);ev.setUint16(20,0,true);
  const result=concat([...localParts,centralBytes,end]);
  if(result.length>MAX_ARCHIVE_BYTES)throw new RangeError("Portable project package exceeds the 528 MiB archive limit");
  return result;
}
function findEnd(bytes,view) {
  const start=Math.max(0,bytes.length-65557);
  for(let p=bytes.length-22;p>=start;p--)if(view.getUint32(p,true)===EOCD)return p;
  throw new TypeError("Invalid ZIP package: end-of-central-directory record is missing");
}
function parseZip(input) {
  const bytes=input instanceof Uint8Array?input:new Uint8Array(input);
  if(bytes.length<22||bytes.length>MAX_ARCHIVE_BYTES)throw new RangeError("Package size is outside the supported limit");
  const view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength),end=findEnd(bytes,view);
  const disk=view.getUint16(end+4,true),centralDisk=view.getUint16(end+6,true);
  const diskCount=view.getUint16(end+8,true),count=view.getUint16(end+10,true);
  const centralSize=view.getUint32(end+12,true),centralOffset=view.getUint32(end+16,true);
  const commentLength=view.getUint16(end+20,true);
  if(disk||centralDisk||diskCount!==count||count>MAX_ENTRIES)throw new TypeError("Multi-disk or oversized ZIP packages are not supported");
  if(count===0xffff||centralSize===0xffffffff||centralOffset===0xffffffff)throw new TypeError("ZIP64 packages are not supported");
  if(end+22+commentLength!==bytes.length||centralOffset+centralSize!==end)throw new TypeError("Invalid ZIP directory bounds");
  const entries=new Map();let cursor=centralOffset;
  for(let i=0;i<count;i++){
    if(cursor+46>end||view.getUint32(cursor,true)!==CENTRAL)throw new TypeError("Invalid ZIP central directory entry");
    const flags=view.getUint16(cursor+8,true),method=view.getUint16(cursor+10,true);
    const crc=view.getUint32(cursor+16,true),compressed=view.getUint32(cursor+20,true);
    const size=view.getUint32(cursor+24,true),nameLength=view.getUint16(cursor+28,true);
    const extraLength=view.getUint16(cursor+30,true),entryComment=view.getUint16(cursor+32,true);
    const startDisk=view.getUint16(cursor+34,true),localOffset=view.getUint32(cursor+42,true);
    const next=cursor+46+nameLength+extraLength+entryComment;
    if(next>end||startDisk!==0||compressed===0xffffffff||size===0xffffffff||localOffset===0xffffffff)throw new TypeError("Unsupported ZIP entry layout");
    if(flags&1)throw new TypeError("Encrypted ZIP entries are not supported");
    if(flags&~0x0800)throw new TypeError("Unsupported ZIP general-purpose flags");
    if(method!==0||compressed!==size)throw new TypeError("Only uncompressed ZIP entries are supported");
    const name=decoder.decode(bytes.subarray(cursor+46,cursor+46+nameLength));
    if(!safePath(name))throw new TypeError("Unsafe or unsupported package path: "+name);
    if(entries.has(name))throw new TypeError("Duplicate package entry: "+name);
    if(localOffset+30>centralOffset||view.getUint32(localOffset,true)!==LOCAL)throw new TypeError("Invalid ZIP local file header");
    const localFlags=view.getUint16(localOffset+6,true),localMethod=view.getUint16(localOffset+8,true);
    const localNameLength=view.getUint16(localOffset+26,true),localExtraLength=view.getUint16(localOffset+28,true);
    const localName=decoder.decode(bytes.subarray(localOffset+30,localOffset+30+localNameLength));
    const dataStart=localOffset+30+localNameLength+localExtraLength,dataEnd=dataStart+size;
    if(localFlags!==flags||localMethod!==method||localName!==name||dataEnd>centralOffset)throw new TypeError("ZIP local and central directory records disagree");
    const data=bytes.slice(dataStart,dataEnd);
    if(crc32(data)!==crc)throw new TypeError("ZIP CRC integrity check failed for "+name);
    entries.set(name,data);cursor=next;
  }
  if(cursor!==end)throw new TypeError("Unexpected data in ZIP central directory");
  return entries;
}
async function sha256(bytes,cryptoImpl) {
  if(!cryptoImpl?.subtle)throw new Error("Web Crypto SHA-256 is unavailable; use a secure browser context");
  const hash=await cryptoImpl.subtle.digest("SHA-256",bytes);
  return Array.from(new Uint8Array(hash),b=>b.toString(16).padStart(2,"0")).join("");
}

export async function createProjectArchive(session,assets,cryptoImpl=globalThis.crypto) {
  const serialized=JSON.stringify(session);
  const validated=decodeSession(serialized);
  if(!Array.isArray(assets)||assets.length!==validated.assets.length)throw new TypeError("Every project asset must be supplied exactly once");
  const supplied=new Map();
  for(const item of assets){
    if(!item||typeof item.id!=="string"||supplied.has(item.id)||!(item.blob instanceof Blob))throw new TypeError("Invalid or duplicate project asset payload");
    supplied.set(item.id,item.blob);
  }
  const names=new Set(["manifest.json"]),entries=[];
  for(const descriptor of validated.assets){
    const path="assets/"+descriptor.storageKey;
    if(!safePath(path)||names.has(path))throw new TypeError("Unsafe or duplicate asset package path");
    names.add(path);
    const blob=supplied.get(descriptor.id);
    if(!blob||blob.size!==descriptor.sizeBytes)throw new TypeError("Project asset is missing or has an unexpected size: "+descriptor.id);
    const bytes=new Uint8Array(await blob.arrayBuffer());
    if(await sha256(bytes,cryptoImpl)!==descriptor.sha256)throw new TypeError("Project asset SHA-256 mismatch: "+descriptor.id);
    entries.push({name:path,bytes});
  }
  if(supplied.size!==validated.assets.length)throw new TypeError("Unexpected project asset payload");
  entries.unshift({name:"manifest.json",bytes:encoder.encode(JSON.stringify(validated,null,2))});
  return new Blob([makeZip(entries)],{type:"application/zip"});
}

export async function readProjectArchive(input,cryptoImpl=globalThis.crypto) {
  const bytes=input instanceof Blob?new Uint8Array(await input.arrayBuffer()):input instanceof ArrayBuffer?new Uint8Array(input):input;
  const entries=parseZip(bytes);
  const manifestBytes=entries.get("manifest.json");
  if(!manifestBytes)throw new TypeError("Portable package is missing manifest.json");
  const session=decodeSession(decoder.decode(manifestBytes));
  const expected=new Set(["manifest.json"]),assets=[];
  for(const descriptor of session.assets){
    const path="assets/"+descriptor.storageKey;
    if(!safePath(path)||expected.has(path))throw new TypeError("Unsafe or duplicate asset path in session manifest");
    expected.add(path);
    const data=entries.get(path);
    if(!data)throw new TypeError("Portable package is missing asset: "+descriptor.id);
    if(data.byteLength!==descriptor.sizeBytes)throw new TypeError("Asset size mismatch: "+descriptor.id);
    if(await sha256(data,cryptoImpl)!==descriptor.sha256)throw new TypeError("Asset SHA-256 mismatch: "+descriptor.id);
    assets.push({id:descriptor.id,blob:new Blob([data],{type:descriptor.mediaType})});
  }
  for(const path of entries.keys())if(!expected.has(path))throw new TypeError("Unexpected file in portable package: "+path);
  return {session,assets};
}
