import sys

sys.stdout.reconfigure(encoding='utf-8')

for path in ['marketing_workflow_app/gsc_ga4_seo_extractor.py', 'marketing_workflow_app/apply_index_updates.py']:
    print(f"=== {path} ===")
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()
    for line in code.splitlines():
        if any(k in line.lower() for k in ['deploy', 'cloudflare', 'git', 'gdrive', 'google drive', 'sync']):
            print(line[:120])
