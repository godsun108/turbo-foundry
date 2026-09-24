#!/usr/bin/env python3
"""Turbo Foundry project scaffolder."""
from __future__ import annotations
import argparse
from pathlib import Path
import re

DIRS=("src","tests","docs","experiments","outputs")

README="""# {name}

Status: EXPERIMENTAL

## Purpose

{purpose}

## Acceptance criteria

Define success before evaluating results.

## Reproducibility

Record input provenance, configuration, code version, and generated outputs.

## Limitations

Document known limitations and uncertainty.
"""

CI="""name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m unittest discover -s tests -v
"""

GITIGNORE="""__pycache__/
*.py[cod]
.venv/
.env
.env.*
outputs/*
!outputs/.gitkeep
"""

SECURITY="""# Security

Never commit credentials, tokens, private keys, recovery phrases, personal identifiers, or sensitive raw data.
"""

CHANGELOG="""# Changelog

## 0.1.0

- Project initialized with Turbo Foundry.
"""

SMOKE="""import unittest

class TestProjectSmoke(unittest.TestCase):
    def test_scaffold_is_alive(self):
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
"""

def slugify(value:str)->str:
    value=re.sub(r"[^A-Za-z0-9._-]+","-",value.strip()).strip("-")
    if not value:
        raise ValueError("project name must contain a usable character")
    return value

def scaffold(name:str,purpose:str,destination:Path)->Path:
    slug=slugify(name)
    root=destination/slug
    if root.exists() and any(root.iterdir()):
        raise FileExistsError(f"Refusing to overwrite non-empty directory: {root}")
    root.mkdir(parents=True,exist_ok=True)
    for d in DIRS:
        (root/d).mkdir(exist_ok=True)
    (root/".github/workflows").mkdir(parents=True,exist_ok=True)
    files={
      "README.md":README.format(name=name,purpose=purpose),
      "CHANGELOG.md":CHANGELOG,
      "SECURITY.md":SECURITY,
      ".gitignore":GITIGNORE,
      ".github/workflows/ci.yml":CI,
      "tests/test_smoke.py":SMOKE,
      "outputs/.gitkeep":"",
      "docs/ARCHITECTURE.md":"# Architecture\n\nDescribe components, boundaries, data flow, and important decisions.\n",
      "experiments/README.md":"# Experiments\n\nState hypotheses and acceptance criteria before evaluating results. Preserve negative results.\n",
    }
    for rel,body in files.items():
        p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(body,encoding="utf-8")
    return root

def main():
    p=argparse.ArgumentParser(description="Generate a Turbo Foundry project")
    p.add_argument("name")
    p.add_argument("--purpose",default="Define the project purpose.")
    p.add_argument("--destination",type=Path,default=Path("."))
    a=p.parse_args()
    print(scaffold(a.name,a.purpose,a.destination))

if __name__=="__main__":
    main()
