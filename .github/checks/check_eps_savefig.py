#!/usr/bin/env python3
import os
import re
import sys

def IsExcludedPath(path, excluded):
    norm = os.path.normpath(path)
    return any(norm == e or norm.startswith(e + os.sep) for e in excluded)

def IsHidden(name):
    return name.startswith(".")

def IsIgnoredDir(name):
    return IsHidden(name) or name == "__pycache__"

def ReadFile(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except Exception:
        return None

def WalkFiles(root, excluded, extension):
    for dir_path, dir_names, file_names in os.walk(root):
        if IsExcludedPath(dir_path, excluded):
            dir_names[:] = []
            continue

        dir_names[:] = [d for d in dir_names if not IsIgnoredDir(d)]

        for file_name in file_names:
            if file_name.endswith(extension) and not IsHidden(file_name):
                yield os.path.join(dir_path, file_name)

def CheckEpsSavefig(content):
    eps_savefig_patterns = [
        r'\.savefig\([^)]*[\'"].*eps.*[\'"][^)]*\)',
        r'\.savefig\([^)]*format\s*=\s*[\'"]eps[\'"][^)]*\)'
    ]

    eps_lines = []
    for line_num, line in enumerate(content.split('\n'), 1):
        for pattern in eps_savefig_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                eps_lines.append(f"Line {line_num}: {line.strip()}")
                break

    remove_count = content.count('remove_eps_info(')
    return eps_lines if len(eps_lines) != remove_count else []

def CollectEpsProblems(root, excluded):
    problems = []
    for file_path in WalkFiles(root, excluded, '.py'):
        content = ReadFile(file_path)
        if content is None:
            continue
        file_problems = CheckEpsSavefig(content)
        if file_problems:
            problems.append({'file': file_path, 'issues': file_problems})
    return problems

def Main():
    source_root   = "source"
    excluded      = ["source/lib", "source/raw", "source/scrape"]

    problems = CollectEpsProblems(source_root, excluded)

    if problems:
        print("EPS savefig check failed!")
        print("\nPython files using .savefig(*eps*) without remove_eps_info():")
        for problem in problems:
            print(f"\nFile: {problem['file']}")
            for issue in problem['issues']:
                print(f"  {issue}")
        print("\nTo fix: Add 'from source.lib.JMSLab.remove_eps_info import remove_eps_info'")
        print("and call 'remove_eps_info(filename)' after each EPS savefig.")
        return 1
    else:
        print("EPS savefig check: all checks passed.")
        return 0

if __name__ == "__main__":
    sys.exit(Main())
