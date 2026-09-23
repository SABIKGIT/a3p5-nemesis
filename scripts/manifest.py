#!/usr/bin/env python3
"""Write/check distribution integrity; UTF-8 text hashes use LF line endings."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "verification/file_manifest.json"
TEXT_SUFFIXES = {".py", ".md", ".json", ".csv", ".svg", ".tex", ".yml", ".yaml", ".cff", ".txt", ".bib", ".cjs", ".html", ".css", ".js", ".toml"}
TEXT_NAMES = {".gitignore", ".gitattributes", ".latexmkrc"}
SKIP_PARTS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache"}
SKIP_PREFIXES = ("manuscript/qa/", "manuscript/python_packages/", "manuscript/tools/", "manuscript/package_staging/")

def excluded(path):
    rel = path.relative_to(ROOT).as_posix()
    return (path == MANIFEST or bool(SKIP_PARTS.intersection(path.relative_to(ROOT).parts))
            or rel.startswith(SKIP_PREFIXES)
            or (rel.startswith("verification/") and path.name.startswith(("local-", "ci-")))
            or path.suffix in {".pyc", ".pyo", ".blend1", ".blend2", ".log", ".tmp", ".aux", ".out", ".fls", ".fdb_latexmk"}
            or path.name.startswith(("~$", ".env")) or path.name in {"Thumbs.db", ".DS_Store"}
            or (rel.startswith(("manuscript/final/", "manuscript/latex/")) and path.parent.name in {"final", "latex"} and path.suffix in {".zip", ".pdf"}))

def files():
    return sorted((p for p in ROOT.rglob("*") if p.is_file() and not excluded(p)), key=lambda p: p.relative_to(ROOT).as_posix())

def record(path):
    data = path.read_bytes()
    text = path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_NAMES
    if text:
        data.decode("utf-8-sig")  # Do not silently normalize binary content.
        data = data.replace(b"\r\n", b"\n")
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(data).hexdigest(),
            "hashed_bytes": len(data), "normalization": "utf8-crlf-to-lf" if text else "none"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="record the current reviewed distribution")
    group.add_argument("--check", action="store_true", help="verify packaged files and detect unexpected files")
    args = parser.parse_args()
    current = [record(p) for p in files()]
    if args.write:
        payload = {"format_version": 1, "scope": "Reviewed distribution files; line-ending differences in UTF-8 text are normalized for Git portability. This manifest excludes itself, generated QA, caches, and local/CI reports.", "files": current}
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"WROTE {len(current)} integrity records")
        return 0
    expected = json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]
    old = {item["path"]: item for item in expected}
    new = {item["path"]: item for item in current}
    issues = (["MISSING " + name for name in sorted(old.keys() - new.keys())]
              + ["UNEXPECTED " + name for name in sorted(new.keys() - old.keys())]
              + ["CHANGED " + name for name in sorted(old.keys() & new.keys()) if old[name] != new[name]])
    for issue in issues:
        print(issue)
    print(f"{'FAIL' if issues else 'PASS'}: {len(expected)} distribution files checked")
    return 1 if issues else 0

if __name__ == "__main__":
    sys.exit(main())
