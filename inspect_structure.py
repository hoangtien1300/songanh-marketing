import json
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=== MARKETING_DATA.JSON item 0 ===")
with open('marketing_workflow_app/marketing_data.json', 'r', encoding='utf-8') as f:
    mdata = json.load(f)

if mdata.get('seo_keywords'):
    print(json.dumps(mdata['seo_keywords'][0], ensure_ascii=False, indent=2))
    print(json.dumps(mdata['seo_keywords'][21], ensure_ascii=False, indent=2))

print("\n=== MASTER CSV row 0 & 21 ===")
df_master = pd.read_csv('marketing_workflow_app/song_anh_seo_keywords_master_dataset.csv', encoding='utf-8')
print("Columns:", list(df_master.columns))
print(df_master.iloc[0].to_dict())
print(df_master.iloc[21].to_dict())

print("\n=== HISTORICAL CSV row 0 & last ===")
df_hist = pd.read_csv('marketing_workflow_app/song_anh_seo_keywords_historical_database.csv', encoding='utf-8')
print("Columns:", list(df_hist.columns))
print("Total historical rows:", len(df_hist))
print(df_hist.iloc[0].to_dict())
