import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('marketing_workflow_app/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("HTML length:", len(html))
for line in html.splitlines():
    if 'xuong-san-xuat' in line or 'mohinhkientruc.org' in line or 'TARGET_KEYWORDS' in line:
        print(line[:120])
