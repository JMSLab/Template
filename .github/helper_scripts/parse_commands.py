#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

def LoadChecks():
    checks_path = Path(__file__).parent.parent / 'checks' / 'checks.json'
    return json.loads(checks_path.read_text())

def ParseCommands():
    checks = LoadChecks()
    comment = os.environ.get('COMMENT_BODY', '')
    return [c['name'] for c in checks
            if os.environ.get('GITHUB_EVENT_NAME') == 'push'
            or '/run-actions-all' in comment
            or c.get('command', '') in comment]

def Main():
    print(json.dumps(ParseCommands()))
    return 0

if __name__ == '__main__':
    sys.exit(Main())
