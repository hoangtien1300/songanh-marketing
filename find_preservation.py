import os, sys

sys.stdout.reconfigure(encoding='utf-8')

for root, dirs, files in os.walk('marketing_workflow_app'):
    for f in files:
        if f.endswith(('.py', '.json', '.html', '.md', '.txt')):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                content = fp.read()
                if 'PRESERVATION' in content or 'preservation' in content:
                    print(f"FOUND in {path}")
