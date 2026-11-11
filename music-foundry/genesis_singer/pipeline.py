"""End-to-end local Genesis Singer score-to-WAV command."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys
from pathlib import Path

def digest(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checkpoint",type=Path,required=True)
    p.add_argument("--score",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--device",choices=("cpu","cuda"),default="cpu")
    p.add_argument("--griffin-lim-iterations",type=int,default=48)
    a=p.parse_args()
    checkpoint=a.checkpoint.expanduser().resolve(); score=a.score.expanduser().resolve(); output=a.output.expanduser().resolve()
    for label,path in (("checkpoint",checkpoint),("score",score)):
        if not path.is_file(): p.error(f"{label} file does not exist: {path}")
    if output.exists(): p.error(f"refusing to overwrite existing output: {output}")
    output.parent.mkdir(parents=True,exist_ok=True)
    command=[sys.executable,"-m","genesis_singer.infer","--checkpoint",str(checkpoint),"--score",str(score),"--output",str(output),"--device",a.device,"--griffin-lim-iterations",str(a.griffin_lim_iterations)]
    result=subprocess.run(command,capture_output=True,text=True,check=False)
    if result.returncode:
        print(result.stdout); print(result.stderr,file=sys.stderr); return result.returncode
    report={"schema":"genesis-singer.pipeline.v1","status":"rendered_experimental","engine":"GenesisSinger","checkpoint":str(checkpoint),"checkpoint_sha256":digest(checkpoint),"score":str(score),"score_sha256":digest(score),"output":str(output),"output_sha256":digest(output),"renderer":"Griffin-Lim baseline; not production neural vocoder","stdout":result.stdout}
    report_path=output.with_suffix(output.suffix+".manifest.json")
    report_path.write_text(json.dumps(report,indent=2)+"\\n",encoding="utf-8")
    print(json.dumps(report,indent=2)); return 0

if __name__=="__main__": raise SystemExit(main())
