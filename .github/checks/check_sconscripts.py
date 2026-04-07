#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path
import tomllib

_EXCEPTIONS_FILE = Path(__file__).parent / "sconscript_exceptions.toml"

def _LoadExceptions():
    with open(_EXCEPTIONS_FILE, "rb") as f:
        data = tomllib.load(f)
    return data.get("excluded_files") or {}, data.get("settings", {}).get("skip_dirs") or []

EXCLUDED_FILES, SKIP_DIRS = _LoadExceptions()

ROOT       = Path("source")
PAPER_DIR  = Path("source/paper")
PAPER_EXTS = {".bib", ".tex", ".lyx"}


def Main():
    missing_dirs, missing_mentions = CollectProblems()
    missing_in_sconstruct = SourceFoldersMissingInSConstruct()
    any_problems = bool(missing_dirs or missing_mentions or missing_in_sconstruct)
    if any_problems:
        print("SConscript/SConstruct summary of missing items:")
        if missing_dirs:
            print("\nFolders missing SConscript:")
            for p in missing_dirs:
                print(p)
        if missing_mentions:
            print("\nFiles not mentioned in their SConscript:")
            for p in missing_mentions:
                print(p)
        if missing_in_sconstruct:
            print("\nTop-level source folders missing from root SConstruct:")
            for p in missing_in_sconstruct:
                print(p)
    else:
        print("SConscript/SConstruct summary: all checks passed.")
    return 1 if any_problems else 0


def CollectProblems():
    missing_dirs     = []
    missing_mentions = []
    exceptions       = set(EXCLUDED_FILES)
    for dir_path, dir_names, file_names in os.walk(ROOT):
        dir_path = Path(dir_path)
        if IsExcluded(dir_path):
            dir_names[:] = []
            continue
        dir_names[:] = sorted(d for d in dir_names if not IsIgnored(d))
        file_names   = [f for f in file_names if not IsIgnored(f)]
        if dir_path == ROOT or (not dir_names and not file_names):
            continue
        content = Read(dir_path / "SConscript")
        if content is None:
            parent_content = Read(dir_path.parent / "SConscript")
            if parent_content is None:
                missing_dirs.append(dir_path)
            continue
        rel = dir_path.relative_to(ROOT).as_posix()
        for f in sorted(f for f in file_names if f != "SConscript"):
            path = f"source/{rel}/{f}"
            if ShouldCheck(dir_path, f) and path not in exceptions and not IsMentioned(content, f, dir_path):
                missing_mentions.append(f"{dir_path} -> {f}")
        for subdir in dir_names:
            if re.search(rf"\b{re.escape(subdir)}\b", content):
                continue
            subdir_path = dir_path / subdir
            try:
                subfiles = sorted(
                    e for e in os.listdir(subdir_path)
                    if not IsIgnored(e) and (subdir_path / e).is_file() and ShouldCheck(subdir_path, e)
                )
            except Exception:
                missing_dirs.append(subdir_path)
                continue
            for f in subfiles:
                if not IsMentioned(content, f, subdir_path):
                    missing_mentions.append(f"{dir_path} -> {subdir}/{f}")
    return missing_dirs, missing_mentions


def IsExcluded(dir_path):
    return any(dir_path == Path(d) or dir_path.is_relative_to(d) for d in SKIP_DIRS)


def IsIgnored(name):
    return name.startswith(".") or name == "__pycache__"


def ShouldCheck(dir_path, name):
    if dir_path.is_relative_to(PAPER_DIR):
        return Path(name).suffix in PAPER_EXTS
    return True


def Read(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception:
        return None


def IsMentioned(content, name, dir_path):
    rel = dir_path.relative_to(ROOT).as_posix()
    return f"#source/{rel}/{name}" in content


def SourceFoldersMissingInSConstruct():
    content = Read("SConstruct")
    folders = sorted(
        e for e in os.listdir(ROOT)
        if (ROOT / e).is_dir() and not IsIgnored(e) and not IsExcluded(ROOT / e)
    )
    if content is None:
        return folders
    return [f for f in folders if f"source/{f}/SConscript" not in content]


if __name__ == "__main__":
    sys.exit(Main())
