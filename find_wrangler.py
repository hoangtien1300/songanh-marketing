import os, re, sys

sys.stdout.reconfigure(encoding='utf-8')

for root, dirs, files in os.walk('marketing_workflow_app'):
    for f in files:
        if f.endswith(('.py', '.json', '.html', '.bat', '.sh')):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                content = fp.read()
                if 'wrangler' in content.lower():
                    print(f"FOUND wrangler in {path}")
