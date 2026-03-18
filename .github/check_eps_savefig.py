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

def CheckEpsSavefig(file_path, content):
    """
    Check if file contains .savefig(*eps*) without remove_eps_info(
    Returns list of problematic lines with line numbers
    """
    problems = []
    lines = content.split('\n')
    
    # Pattern to match .savefig with eps format (both single and double quotes)
    eps_savefig_patterns = [
        r'\.savefig\([^)]*[\'"].*eps.*[\'"][^)]*\)',  # matches .savefig(...'...eps...'...)
        r'\.savefig\([^)]*format\s*=\s*[\'"]eps[\'"][^)]*\)'  # matches format='eps' or format="eps"
    ]
    
    has_remove_eps_info = 'remove_eps_info(' in content
    
    for line_num, line in enumerate(lines, 1):
        for pattern in eps_savefig_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                if not has_remove_eps_info:
                    problems.append(f"Line {line_num}: {line.strip()}")
                break
    
    return problems

def CollectEpsProblems(root, excluded):
    """Walk through Python files and check for EPS savefig issues"""
    problems = []
    
    for dir_path, dir_names, file_names in os.walk(root):
        if IsExcludedPath(dir_path, excluded):
            dir_names[:] = []
            continue
            
        dir_names[:] = [d for d in dir_names if not IsIgnoredDir(d)]
        
        for file_name in file_names:
            if not file_name.endswith('.py'):
                continue
                
            if IsHidden(file_name):
                continue
                
            file_path = os.path.join(dir_path, file_name)
            content = ReadFile(file_path)
            
            if content is None:
                continue
                
            file_problems = CheckEpsSavefig(file_path, content)
            if file_problems:
                problems.append({
                    'file': file_path,
                    'issues': file_problems
                })
    
    return problems

def CheckEpsCreationDate(content):
    """
    Check if any line in an EPS file starts with %%CreationDate.
    Returns True if it does.
    """
    return any(line.startswith("%%CreationDate") for line in content.splitlines())

def CollectEpsCreationDateProblems(root, excluded):
    """Walk through EPS files and report those that contain %%CreationDate"""
    eps_files = []
    
    for dir_path, dir_names, file_names in os.walk(root):
        if IsExcludedPath(dir_path, excluded):
            dir_names[:] = []
            continue
            
        dir_names[:] = [d for d in dir_names if not IsIgnoredDir(d)]
        
        for file_name in file_names:
            if not file_name.endswith('.eps'):
                continue
                
            if IsHidden(file_name):
                continue
                
            eps_path = os.path.join(dir_path, file_name)
            content = ReadFile(eps_path)
            
            if content is None:
                continue
                
            if CheckEpsCreationDate(content):
                eps_files.append(eps_path)
    
    return eps_files

def main():
    source_root   = "source"
    output_root   = "output"
    excluded      = ["source/lib", "source/raw", "source/scrape"]

    problems = CollectEpsProblems(source_root, excluded)
    creationdate_eps_files = CollectEpsCreationDateProblems(output_root, [])
    
    if creationdate_eps_files:
        print("EPS files containing %%CreationDate:")
        for eps_file in creationdate_eps_files:
            print(f"  {eps_file}")
        print("")
        return 1

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
    sys.exit(main())