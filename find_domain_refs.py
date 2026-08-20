import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

for root, dirs, files in os.walk('marketing_workflow_app'):
    for f in files:
        if f.endswith(('.py', '.json', '.html', '.csv', '.js', '.bat', '.gs', '.xlsx')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                    if 'mohinhkientruc.org' in content:
                        count = content.count('mohinhkientruc.org')
                        print(f"{path}: {count} occurrences of mohinhkientruc.org")
            except Exception as e:
                print(f"Error reading {path}: {e}")
