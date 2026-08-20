import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=== GSC_GA4_SEO_EXTRACTOR.PY ===")
with open('marketing_workflow_app/gsc_ga4_seo_extractor.py', 'r', encoding='utf-8') as f:
    extractor_code = f.read()

match = re.search(r'TARGET_KEYWORDS_DATA\s*=\s*\[(.*?)\]', extractor_code, re.DOTALL)
if match:
    print("Found TARGET_KEYWORDS_DATA snippet:")
    print(match.group(0)[:800])

match2 = re.search(r'const TARGET_KEYWORDS\s*=\s*\[(.*?)\];', extractor_code, re.DOTALL)
if match2:
    print("Found JS TARGET_KEYWORDS snippet:")
    print(match2.group(0)[:800])

print("\n=== UPDATE_SEO_DATA.PY ===")
with open('marketing_workflow_app/update_seo_data.py', 'r', encoding='utf-8') as f:
    update_code = f.read()

match3 = re.search(r'TARGET_KEYWORDS\s*=\s*\[(.*?)\]', update_code, re.DOTALL)
if match3:
    print("Found TARGET_KEYWORDS in update_seo_data.py:")
    print(match3.group(0)[:800])
