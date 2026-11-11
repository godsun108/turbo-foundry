"""Train Genesis Singer on rights-cleared, phoneme/MIDI-aligned singing WAVs."""
from __future__ import annotations
import argparse,json,random
from pathlib import Path
import torch
from torch.nn import functional as F
from torch.utils.data import DataLoader
from .data import SingingDataset
from .model import GenesisSinger
from .audio import SAMPLE_RATE,HOP,MEL_BINS

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--manifest",type=Path,required=True); p.add_argument("--vocab",type=Path,required=True); p.add_argument("--output",type=Path,required=True); p.add_argument("--speakers",type=int,default=1); p.add_argument("--epochs",type=int,default=100); p.add_argument("--hidden",type=int,default=256); p.add_argument("--layers",type=int,default=4); p.add_argument("--heads",type=int,default=4); p.add_argument("--lr",type=float,default=2e-4); p.add_argument("--seed",type=int,default=17); p.add_argument("--device",choices=("cpu","cuda"),default="cpu"); a=p.parse_args()
    if a.epochs<1 or a.speakers<1 or a.lr<=0: p.error("epochs, speakers and learning rate must be positive")
    if a.device=="cuda" and not torch.cuda.is_available(): p.error("CUDA requested but unavailable")
    random.seed(a.seed); torch.manual_seed(a.seed); vocab=json.loads(a.vocab.read_text(encoding="utf-8"))
    if not isinstance(vocab,dict) or not vocab or any(not isinstance(v,int) or v<1 for v in vocab.values()) or len(set(vocab.values()))!=len(vocab): p.error("vocab must map tokens to unique positive integer IDs")
    ds=SingingDataset(a.manifest,max(vocab.values())+1,a.speakers); loader=DataLoader(ds,batch_size=1,shuffle=True); device=torch.device(a.device)
    model=GenesisSinger(max(vocab.values())+1,a.speakers,MEL_BINS,a.hidden,a.layers,a.heads).to(device); opt=torch.optim.AdamW(model.parameters(),lr=a.lr,betas=(0.9,0.98),weight_decay=1e-4); a.output.mkdir(parents=True,exist_ok=True); best=float("inf")
    for epoch in range(1,a.epochs+1):
        model.train(); losses=[]
        for b in loader:
            b={k:v.to(device) for k,v in b.items()}; opt.zero_grad(set_to_none=True)
            pred=model(b["phoneme_ids"],b["pitches"],b["note_types"],b["durations"],b["speaker_id"].view(1)); target=b["mel"]
            if pred.shape!=target.shape: raise RuntimeError(f"alignment mismatch: {tuple(pred.shape)} vs {tuple(target.shape)}")
            loss=F.l1_loss(pred,target)+0.5*F.mse_loss(pred,target); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),1.0); opt.step(); losses.append(float(loss.detach().cpu()))
        mean=sum(losses)/len(losses); state={"schema":"genesis-singer.checkpoint.v1","epoch":epoch,"model":model.state_dict(),"optimizer":opt.state_dict(),"vocab":vocab,"speakers":a.speakers,"config":{"hidden":a.hidden,"layers":a.layers,"heads":a.heads,"mel_bins":MEL_BINS,"sample_rate":SAMPLE_RATE,"hop":HOP},"training":{"manifest":str(a.manifest.resolve()),"samples":len(ds),"consent_ids":sorted({str(r["consent_id"]) for r in ds.rows}),"loss_l1_plus_0_5_mse":mean}}
        torch.save(state,a.output/"latest.pt")
        if mean<best: best=mean; torch.save(state,a.output/"best.pt")
        (a.output/"training.json").write_text(json.dumps({"epoch":epoch,"loss":mean,"best_loss":best},indent=2)+"\n",encoding="utf-8"); print(f"epoch={epoch} loss={mean:.5f} best={best:.5f}")
    return 0
if __name__=="__main__": raise SystemExit(main())
