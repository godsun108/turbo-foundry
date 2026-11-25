import test from "node:test";
import assert from "node:assert/strict";
import {
  validateAudioClip,validateAudioClipList,splitAudioClip,trimAudioClip,
  moveAudioClip,duplicateAudioClip,setAudioClipLoop
} from "../earth-studio/audio-clip-model.mjs";
const clip=()=>({id:"clip-a",assetId:"asset-a",startSeconds:4,sourceStartSeconds:2,durationSeconds:10});
const ids=(()=>{let n=0;return ()=>"clip-"+(++n)})();
test("validates a source-backed audio clip and unique clip IDs",()=>{
 assert.deepEqual(validateAudioClip(clip()),[]);
 assert.deepEqual(validateAudioClipList([clip(),{...clip(),id:"clip-b"}]),[]);
 assert.ok(validateAudioClipList([clip(),clip()]).some(e=>e.includes("unique")));
});
test("splitting creates two timeline clips that reference contiguous source ranges",()=>{
 const [left,right]=splitAudioClip(clip(),9,ids);
 assert.equal(left.startSeconds,4);assert.equal(left.durationSeconds,5);
 assert.equal(right.startSeconds,9);assert.equal(right.sourceStartSeconds,7);assert.equal(right.durationSeconds,5);
 assert.equal(left.assetId,right.assetId);
 assert.throws(()=>splitAudioClip(clip(),4,ids),RangeError);
});
test("trimming is non-destructive and advances the source offset",()=>{
 const trimmed=trimAudioClip(clip(),{leftSeconds:1.5,rightSeconds:2});
 assert.equal(trimmed.startSeconds,5.5);assert.equal(trimmed.sourceStartSeconds,3.5);assert.equal(trimmed.durationSeconds,6.5);
 assert.equal(clip().sourceStartSeconds,2);
 assert.throws(()=>trimAudioClip(clip(),{leftSeconds:10}),RangeError);
});
test("moving changes only the timeline position",()=>{
 const moved=moveAudioClip(clip(),20);
 assert.equal(moved.startSeconds,20);assert.equal(moved.sourceStartSeconds,2);
 assert.throws(()=>moveAudioClip(clip(),-1),RangeError);
});
test("duplicating creates a distinct instance over the same source asset",()=>{
 const copy=duplicateAudioClip(clip(),{idFactory:ids,offsetSeconds:3});
 assert.notEqual(copy.id,clip().id);assert.equal(copy.startSeconds,7);assert.equal(copy.assetId,"asset-a");
});
test("loop state is explicit and validated",()=>{
 assert.equal(setAudioClipLoop(clip(),true).loop,true);
 assert.throws(()=>setAudioClipLoop(clip(),"yes"),TypeError);
});
