import sys

sys.stdout.reconfigure(encoding='utf-8')

for filepath in [
    'marketing_workflow_app/update_all_system_files.py',
    '01_Mo_Hinh_Kien_Truc/Agents/Master_Marketing_Agent/deploy_seo_dashboard_to_cf_pages.py',
    '01_Mo_Hinh_Kien_Truc/Agents/Master_Marketing_Agent/copy_seomenu_app_to_gdrive.py',
    '01_Mo_Hinh_Kien_Truc/Agents/Master_Marketing_Agent/push_to_github_seo.py'
]:
    print(f"=== {filepath} ===")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            print(f.read()[:1500])
    except Exception as e:
        print(f"Error: {e}")
