# -*- coding: utf-8 -*-
"""
Script: auto_post_gbp_song_anh.py
Tự động hóa đăng bài lên Google Business Profile (GBP) Dịch vụ làm mô hình kiến trúc Song Anh
- NGUYÊN TẮC BẤT DI BẤT DỊCH: 100% TRUNG THỰC DỮ LIỆU. TUYỆT ĐỐI KHÔNG SINH LINK GIẢ LẬP / MOCK LINK.
- Chỉ cập nhật Notion khi trích xuất được link share thật từ Google (https://share.google/... hoặc https://posts.gle/...).
- Nếu Google chặn hoặc không lấy được link thực tế, dừng lại và thông báo trung thực để chuyển sang chế độ hỗ trợ thủ công.
"""

import os
import sys
import io
import time
import json
import random
import requests
import urllib.request
import pyperclip
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 🎯 CẤU HÌNH NOTION
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "ntn_" + "202316998566adC5moVwLDu5vZcjHFYLKdcPcvKO1mq1uE")
NOTION_VERSION = "2022-06-28"
CONTENT_DB_ID = "33d4b5e73d90809faebfd11a9a8b0c0e"
ACTIVITY_LOG_DB_ID = "3c24b5e73d9081b4b505f85f9c9bfcae"

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

# 🎯 CẤU HÌNH GBP KÊNH 1
GBP_LOCATION = {
    "name": "Dịch vụ làm mô hình kiến trúc Song Anh (Thủ Đức)",
    "id": "9117009748298497216",
    "url": "https://www.google.com/local/business/9117009748298497216/promote/updates?knm=0&ih=lu&origin=https://www.google.com&hl=vi",
    "hotline": "0929 22 4444",
    "default_website": "https://www.mohinhkientruc.org"
}

TOPIC_LANDING_PAGES = [
    (["quy hoạch", "đô thị", "phân khu", "bản đồ quy hoạch"], "https://www.mohinhkientruc.org/mo-hinh-quy-hoach/"),
    (["nhà máy", "nhà xưởng", "khu công nghiệp", "kcn", "logistics"], "https://www.mohinhkientruc.org/mo-hinh-nha-may/"),
    (["trường học", "rmit", "uts", "đại học", "giáo dục"], "https://www.mohinhkientruc.org/lam-sa-ban-truong-hoc/"),
    (["tod", "metro", "tuyến metro", "nhà ga"], "https://www.mohinhkientruc.org/mo-hinh-tod-sa-ban/"),
    (["sửa chữa", "bảo dưỡng", "phục hồi", "nâng cấp led", "thay đèn"], "https://www.mohinhkientruc.org/sua-chua-mo-hinh-kien-truc/"),
    (["chung cư", "cao tầng", "căn hộ", "khải hoàn", "prime"], "https://mohinhkientruc.org/sa-ban-cao-tang/"),
    (["thủy sản", "hồ nuôi", "triển lãm", "báo giá", "kiến trúc"], "https://www.mohinhkientruc.org/mo-hinh-kien-truc/")
]

PROFILE_DIR = r"D:\Song_Anh\_Shared_Core\Credentials\gbp_chrome_profile"
DOWNLOAD_DIR = r"D:\Song_Anh\01_Mo_Hinh_Kien_Truc\Project_Assets"

SET_REACT_TEXTAREA_JS = """
var textarea = arguments[0];
var text = arguments[1];
textarea.focus();
var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
nativeInputValueSetter.call(textarea, text);
textarea.dispatchEvent(new Event('input', { bubbles: true }));
textarea.dispatchEvent(new Event('change', { bubbles: true }));
textarea.dispatchEvent(new Event('keyup', { bubbles: true }));
textarea.dispatchEvent(new Event('blur', { bubbles: true }));
"""

CLICK_CTA_OPTION_LEAF_JS = """
var targetText = arguments[0];
var elems = document.querySelectorAll('div, span, li');
var clicked = false;
for (var i = 0; i < elems.length; i++) {
    var txt = (elems[i].textContent || elems[i].innerText || "").trim();
    if (txt === targetText && elems[i].children.length === 0 && elems[i].offsetWidth > 0) {
        elems[i].click();
        clicked = true;
        break;
    }
}
return clicked;
"""

def extract_smart_landing_page(title, content, rollup_url):
    """Trích xuất link landing page phù hợp nhất theo ngữ cảnh"""
    if rollup_url and rollup_url.startswith("http"):
        return rollup_url

    search_text = (title + " " + content).lower()
    for keywords, target_url in TOPIC_LANDING_PAGES:
        for kw in keywords:
            if kw in search_text:
                return target_url

    return "https://www.mohinhkientruc.org/mo-hinh-kien-truc/"

def fetch_candidate_post_from_notion():
    """Lọc bài viết từ trên xuống theo Ngày viết chưa đăng GBP Kênh 1"""
    print("[1] Đang truy vấn Notion DB 'BẢNG CONTENT'...")
    body = {
        "sorts": [
            {
                "property": "Ngày viết",
                "direction": "descending"
            }
        ],
        "page_size": 20
    }
    
    res = requests.post(f"https://api.notion.com/v1/databases/{CONTENT_DB_ID}/query", headers=NOTION_HEADERS, json=body)
    if res.status_code != 200:
        print(f"❌ Lỗi truy vấn Notion: {res.status_code} - {res.text}")
        return None

    results = res.json().get("results", [])
    for page in results:
        props = page["properties"]
        
        gbp_link = props.get("Link GBP (Dịch vụ làm mô hình kiến trúc Song Anh)", {}).get("url")
        gbp_date = props.get("Ngày đăng GBP (Dịch vụ làm mô hình kiến trúc Song Anh)", {}).get("date")

        title_objs = props.get("Tiêu đề bài viết", {}).get("title", [])
        title = "".join([t.get("plain_text", "") for t in title_objs]).strip()

        # Spin GBP text
        spin_objs = props.get("Spin - GBP Dịch vụ làm mô hình kiến trúc Song Anh", {}).get("rich_text", [])
        spin_text = "".join([t.get("plain_text", "") for t in spin_objs]).strip()

        if not spin_text:
            fb_objs = props.get("Spin - Fanpage FB", {}).get("rich_text", [])
            spin_text = "".join([t.get("plain_text", "") for t in fb_objs]).strip()
        if not spin_text:
            orig_objs = props.get("Nội dung gốc", {}).get("rich_text", [])
            spin_text = "".join([t.get("plain_text", "") for t in orig_objs]).strip()

        img_files = props.get("Hình ảnh", {}).get("files", [])
        img_urls = [f.get("file", {}).get("url") or f.get("external", {}).get("url") for f in img_files]

        vid_files = props.get("Video", {}).get("files", [])
        vid_urls = [f.get("file", {}).get("url") or f.get("external", {}).get("url") for f in vid_files]

        yt_url = props.get("Link Video YouTube Channel", {}).get("url")

        rollup_url = None
        rollup_prop = props.get("Link mohinhkientruc.org", {})
        if rollup_prop.get("type") == "rollup":
            arr = rollup_prop.get("rollup", {}).get("array", [])
            for item in arr:
                if item.get("type") == "url":
                    rollup_url = item.get("url")
                    break

        website_link = extract_smart_landing_page(title, spin_text, rollup_url)

        if not gbp_link or not gbp_date:
            print(f"✅ Chọn bài viết: [{title}] (Page ID: {page['id']})")
            return {
                "page_id": page["id"],
                "title": title,
                "content": spin_text,
                "img_urls": img_urls,
                "vid_urls": vid_urls,
                "yt_url": yt_url,
                "website_link": website_link
            }

    print("⚠️ Tất cả các bài viết trong danh sách đã được đăng GBP!")
    return None

def resolve_media_and_cta_rules(post_data):
    """Áp dụng Quy tắc Media & Nút CTA chuẩn (100% Không dùng nút Gọi ngay)"""
    has_img = len(post_data.get("img_urls", [])) > 0
    has_vid = len(post_data.get("vid_urls", [])) > 0
    has_yt = bool(post_data.get("yt_url"))

    local_media_path = None
    cta_option = "Tìm hiểu thêm"
    cta_url = post_data.get("website_link")

    if has_img and has_yt:
        local_media_path = download_media_file(post_data["img_urls"][0], "img")
        choice = random.choice(["website", "youtube"])
        cta_url = post_data.get("website_link") if choice == "website" else post_data["yt_url"]
    elif has_img:
        local_media_path = download_media_file(post_data["img_urls"][0], "img")
    elif has_vid and not has_img:
        local_media_path = download_media_file(post_data["vid_urls"][0], "vid")
    elif has_yt and not has_img and not has_vid:
        cta_url = post_data["yt_url"]

    return local_media_path, cta_option, cta_url

def download_media_file(url, media_type="img"):
    """Tải file từ Google Drive link hoặc URL trực tiếp"""
    if not url:
        return None
    
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    ext = ".jpg" if media_type == "img" else ".mp4"
    
    file_id = "temp_media"
    if "drive.google.com" in url:
        if "/file/d/" in url:
            file_id = url.split("/file/d/")[1].split("/")[0].split("?")[0]
        elif "id=" in url:
            file_id = url.split("id=")[1].split("&")[0]
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    else:
        download_url = url

    save_path = os.path.join(DOWNLOAD_DIR, f"gbp_{file_id}{ext}")
    if os.path.exists(save_path):
        return save_path

    try:
        req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp, open(save_path, 'wb') as f:
            f.write(resp.read())
        return save_path
    except Exception as e:
        print(f"⚠️ Lỗi tải media: {e}")
        return None

def publish_to_gbp(content_text, media_path=None, cta_option="Tìm hiểu thêm", cta_url=None):
    """Thực thi đăng bài và chỉ trả về link thật từ Google"""
    options = Options()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    real_share_link = None

    try:
        driver.get(GBP_LOCATION["url"])
        time.sleep(5)

        plus_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Thêm bài đăng')]")
        driver.execute_script("arguments[0].click();", plus_btn)
        time.sleep(3)

        tas = driver.find_elements(By.XPATH, "//textarea")
        if tas:
            driver.execute_script(SET_REACT_TEXTAREA_JS, tas[0], content_text[:1450])
            time.sleep(2)

        if media_path and os.path.exists(media_path):
            file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            if file_inputs:
                file_inputs[0].send_keys(media_path)
                time.sleep(5)

        plus_nut = driver.find_elements(By.XPATH, "//button[@aria-label='Thêm trường đường liên kết'] | //button[contains(., 'Nút')]")
        if plus_nut and plus_nut[0].is_displayed():
            driver.execute_script("arguments[0].click();", plus_nut[0])
            time.sleep(2)

        khong_box = driver.find_elements(By.XPATH, "//*[text()='Không']")
        if khong_box and khong_box[0].is_displayed():
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", khong_box[0])
            driver.execute_script("arguments[0].click();", khong_box[0])
            time.sleep(1.5)

        driver.execute_script(CLICK_CTA_OPTION_LEAF_JS, cta_option)
        time.sleep(2)

        inps = driver.find_elements(By.XPATH, "//input[@type='text' or @type='url' or not(@type)]")
        for inp in reversed(inps):
            if inp.is_displayed() and inp.tag_name == 'input' and inp.get_attribute("type") != "file":
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
                inp.click()
                time.sleep(0.3)
                inp.send_keys(Keys.CONTROL + "a")
                inp.send_keys(Keys.BACKSPACE)
                time.sleep(0.2)
                for ch in cta_url:
                    inp.send_keys(ch)
                    time.sleep(0.01)
                time.sleep(0.3)
                inp.send_keys(Keys.TAB)
                time.sleep(1.5)
                break

        submit_btn = driver.find_element(By.XPATH, "//button[contains(., 'Bài đăng') or contains(., 'Đăng')]")
        submit_btn.click()
        time.sleep(10)

        # Trích xuất link thực tế
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[value*='share.google'], input[value*='posts.gle']")
        for inp in inputs:
            v = inp.get_attribute("value")
            if v and ("share.google" in v or "posts.gle" in v):
                real_share_link = v.strip()
                break

        if not real_share_link:
            copy_btns = driver.find_elements(By.XPATH, "//*[contains(text(), 'Sao chép') or contains(text(), 'Copy')]")
            for cb in copy_btns:
                if cb.is_displayed():
                    driver.execute_script("arguments[0].click();", cb)
                    time.sleep(1)
                    clip = pyperclip.paste()
                    if clip and ("share.google" in clip or "posts.gle" in clip):
                        real_share_link = clip.strip()
                        break

        # Bỏ qua popup
        bo_qua_btns = driver.find_elements(By.XPATH, "//*[contains(text(), 'Bỏ qua') or contains(text(), 'Xong')]")
        for bq in bo_qua_btns:
            if bq.is_displayed():
                driver.execute_script("arguments[0].click();", bq)
                time.sleep(2)
                break

        if real_share_link:
            return True, real_share_link
        else:
            print("⚠️ Cảnh báo: Google chưa trả về link chia sẻ hợp lệ!")
            return False, None

    except Exception as e:
        print(f"❌ Lỗi xuất bản: {e}")
        return False, None
    finally:
        driver.quit()

def update_notion_published_status(page_id, post_link):
    """Chỉ cập nhật Notion khi có link thật 100%"""
    if not post_link or "share.google/r8k" in post_link or "error" in post_link:
        print("🛑 Không cập nhật Notion vì không có link thật!")
        return False

    today_str = datetime.now().strftime("%Y-%m-%d")
    body = {
        "properties": {
            "Link GBP (Dịch vụ làm mô hình kiến trúc Song Anh)": {
                "url": post_link
            },
            "Ngày đăng GBP (Dịch vụ làm mô hình kiến trúc Song Anh)": {
                "date": {
                    "start": today_str
                }
            }
        }
    }
    res = requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=NOTION_HEADERS, json=body)
    return res.status_code == 200

def main():
    print("="*80)
    print("🚀 TOOL AUTOMATION ĐĂNG BÀI GOOGLE BUSINESS PROFILE (GBP) SONG ANH 🚀")
    print("🔒 NGUYÊN TẮC: 100% TRUNG THỰC DỮ LIỆU - CHỈ LƯU LINK GOOGLE THẬT")
    print("="*80)

    post = fetch_candidate_post_from_notion()
    if not post:
        print("[-] Kết thúc: Không có bài viết nào cần xuất bản.")
        return

    media_path, cta_option, cta_url = resolve_media_and_cta_rules(post)
    success, post_link = publish_to_gbp(post["content"], media_path, cta_option, cta_url)

    if success and post_link:
        update_notion_published_status(post["page_id"], post_link)
        print(f"🎉 Xuất bản thành công với link thật: {post_link}")
    else:
        print("🛑 Chưa lấy được link thật từ Google. Cần thực hiện kiểm tra thủ công.")

if __name__ == "__main__":
    main()
