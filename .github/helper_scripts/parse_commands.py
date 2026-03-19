import json, os
checks  = json.load(open(os.path.join(os.path.dirname(__file__), '../checks/checks.json')))
comment = os.environ.get('COMMENT_BODY', '')
run = [c['name'] for c in checks
       if os.environ.get('GITHUB_EVENT_NAME') == 'push'
       or '/run-actions-all' in comment
       or c.get('command', '') in comment]
print(json.dumps(run))
