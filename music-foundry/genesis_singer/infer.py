"""Render score JSON to WAV with a trained Genesis Singer checkpoint."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import torch,soundfile as sf
from .model import GenesisSinger
from .audio import SAMPLE_RATE,mel_to_wav

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--checkpoint",type=Path,required=True); p.add_argument("--score",type=Path,required=True); p.add_argument("--output",type=Path,required=True); p.add_argument("--device",choices=("cpu","cuda"),default="cpu"); p.add_argument("--griffin-lim-iterations",type=int,default=48); a=p.parse_args()
    if a.device=="cuda" and not torch.cuda.is_available(): p.error("CUDA requested but unavailable")
    device=torch.device(a.device); ckpt=torch.load(a.checkpoint,map_location=device,weights_only=False)
    if ckpt.get("schema")!="genesis-singer.checkpoint.v1": p.error("unsupported checkpoint schema")
    score=json.loads(a.score.read_text(encoding="utf-8")); vocab=ckpt["vocab"]
    try: ids=[int(vocab[t]) for t in score["phonemes"]]
    except (KeyError,TypeError) as exc: p.error(f"phoneme missing from model vocabulary: {exc}")
    pitches=score["pitches"]; types=score["note_types"]; durations=score["durations_frames"]
    if not ids or not (len(ids)==len(pitches)==len(types)==len(durations)) or any(int(d)<1 for d in durations): p.error("score arrays must be non-empty, aligned and have positive frame durations")
    model=GenesisSinger(len(vocab)+1,ckpt["speakers"],ckpt["config"]["mel_bins"],ckpt["config"]["hidden"],ckpt["config"]["layers"],ckpt["config"]["heads"]).to(device); model.load_state_dict(ckpt["model"]); model.eval()
    with torch.no_grad():
        mel=model(torch.tensor([ids],device=device),torch.tensor([pitches],device=device),torch.tensor([types],device=device),torch.tensor([durations],device=device),torch.tensor([int(score.get("speaker_id",0))],device=device))[0]
        wav=mel_to_wav(mel,a.griffin_lim_iterations).cpu().numpy()
    a.output.parent.mkdir(parents=True,exist_ok=True); sf.write(str(a.output),wav,SAMPLE_RATE,subtype="PCM_16")
    print(json.dumps({"status":"rendered_experimental","output":str(a.output),"sample_rate":SAMPLE_RATE,"duration_seconds":len(wav)/SAMPLE_RATE,"decoder":"Griffin-Lim baseline; not production neural vocoder"},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
