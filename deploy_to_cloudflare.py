# -*- coding: utf-8 -*-
"""
Cloudflare Workers & Static Assets Deployment Script
Directly calls Cloudflare Client v4 API to upload assets & deploy script.
"""
import os
import sys
import json
import base64
import hashlib
import requests
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ACCOUNT_ID = "93a916b0e5067e0d2769d0807bebe77e"
API_TOKEN = os.environ.get("CF_API_TOKEN") or base64.b64decode("Y2Z1dF9VVHpTMk1va2Q2anIyMlpOcHltZlV1clBXMzNPemFpcGNUYmFLNXBQYTU5OWY5NDk=").decode("utf-8")
SCRIPT_NAME = "songanh-marketing"
APP_DIR = r"d:\Song_Anh\marketing_workflow_app"

def deploy():
    print(f"🚀 Bắt đầu Deploy Cloudflare Workers: {SCRIPT_NAME}")
    
    # 1. Scan files for assets manifest
    manifest = {}
    files_to_hash = {}
    
    # Excluded extensions or patterns
    excluded_exts = {'.py', '.pyc', '.bat', '.sh', '.gs'}
    excluded_dirs = {'.git', '__pycache__', '.github'}
    
    for root, dirs, files in os.walk(APP_DIR):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in excluded_exts:
                continue
            if f in ('worker.js', 'wrangler.jsonc', 'telegram_config.json', 'facebook_credentials.json', 'service_account.json'):
                continue
            
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, APP_DIR).replace('\\', '/')
            
            with open(full_path, 'rb') as fp:
                data = fp.read()
            
            # Hash must be 32 hex chars (16 bytes = 32 hex characters of sha256)
            h = hashlib.sha256(data).hexdigest()[:32]
            manifest['/' + rel_path] = {
                'hash': h,
                'size': len(data)
            }
            files_to_hash[h] = data

    print(f"📦 Đã quét {len(manifest)} static assets.")
    
    # 2. Create assets upload session
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    session_url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/workers/scripts/{SCRIPT_NAME}/assets-upload-session"
    
    print("⏳ Đang khởi tạo session upload assets...")
    session_res = requests.post(session_url, headers=headers, json={'manifest': manifest})
    if session_res.status_code != 200:
        print(f"❌ Khởi tạo session thất bại ({session_res.status_code}): {session_res.text}")
        return False
    
    session_data = session_res.json()
    result = session_data.get('result', {})
    jwt = result.get('jwt')
    buckets = result.get('buckets', [])
    
    print(f"🔑 Nhận JWT thành công. Cần upload {len(buckets)} buckets.")
    
    completion_jwt = jwt
    upload_url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/workers/assets/upload?base64=true"
    for i, bucket in enumerate(buckets, 1):
        print(f"📤 Đang upload bucket {i}/{len(buckets)} ({len(bucket)} files)...")
        files_payload = {}
        for h in bucket:
            b64_str = base64.b64encode(files_to_hash[h]).decode('utf-8')
            files_payload[h] = (None, b64_str)
        
        up_res = requests.post(
            upload_url,
            headers={'Authorization': f'Bearer {jwt}'},
            files=files_payload
        )
        if up_res.status_code not in (200, 201, 202):
            print(f"❌ Lỗi upload bucket {i} ({up_res.status_code}): {up_res.text}")
            return False
        
        res_jwt = up_res.json().get('result', {}).get('jwt')
        if res_jwt:
            completion_jwt = res_jwt
        print(f"   ✅ Bucket {i} uploaded thành công ({up_res.status_code}).")
    
    # 4. Upload script and bind assets
    print(f"🚀 Đang cập nhật Worker Script với completion JWT...")
    worker_path = os.path.join(APP_DIR, 'worker.js')
    with open(worker_path, 'r', encoding='utf-8') as f:
        worker_code = f.read()
    
    metadata = {
        "main_module": "worker.js",
        "compatibility_date": "2026-08-19",
        "compatibility_flags": ["nodejs_compat"],
        "assets": {
            "jwt": completion_jwt
        },
        "bindings": [
            {
                "name": "ASSETS",
                "type": "assets"
            }
        ]
    }
    
    put_url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/workers/scripts/{SCRIPT_NAME}"
    script_files = {
        'metadata': (None, json.dumps(metadata), 'application/json'),
        'worker.js': ('worker.js', worker_code, 'application/javascript+module')
    }
    
    put_res = requests.put(
        put_url,
        headers={'Authorization': f'Bearer {API_TOKEN}'},
        files=script_files
    )
    
    if put_res.status_code == 200:
        print("🎉 DEPLOY THÀNH CÔNG LÊN CLOUDFLARE WORKERS!")
        print(f"🌐 Live URL: https://songanh-marketing.phamhoangtien1300.workers.dev/#tasks")
        return True
    else:
        print(f"❌ Deploy thất bại ({put_res.status_code}): {put_res.text}")
        return False

if __name__ == "__main__":
    deploy()
