"""Manual/imported JSON adapter.

This is the first released adapter. Future adapters must use permitted APIs,
licensed feeds, or public-record sources rather than brittle/unauthorized scraping.
"""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]))
from scout import Candidate

def load_candidates(path:str|Path)->list[Candidate]:
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data,list): raise ValueError("candidate file must contain a JSON list")
    return [Candidate(**x) for x in data]
