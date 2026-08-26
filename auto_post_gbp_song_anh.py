# -*- coding: utf-8 -*-
"""
Script: auto_post_gbp_song_anh.py
Tự động hóa đăng bài lên Google Business Profile (GBP) Dịch vụ làm mô hình kiến trúc Song Anh
- Kết nối trực tiếp Notion Database 'BẢNG CONTENT' (33d4b5e7-3d90-809f-aebf-d11a9a8b0c0e)
- Xử lý link đích ngữ cảnh thông minh (Dynamic Contextual Landing Page): Tùy theo chủ đề bài viết mà trỏ đúng URL bài viết chuyên sâu trên website (không trỏ cứng 1 link trang chủ).
- 100% Nút 'Tìm hiểu thêm' (Website / YouTube) - Không dùng nút 'Gọi ngay' cho kênh Mô hình.
- Cập nhật Link và Ngày đăng GBP ngược lại vào Notion
- Đồng bộ nhật ký hoạt động sang Database 'NHẬT KÝ THAO TÁC MARKETING SONG ANH'
"""

import os
import sys
import io
import time
import json
import random
import requests
import urllib.request
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
    "profile_url": "https://business.google.com/n/9117009748298497216/profile?fid=4501860915618316199",
    "url": "https://www.google.com/local/business/9117009748298497216/promote/updates?knm=0&ih=lu&origin=https://www.google.com&hl=vi",
    "hotline": "0929 22 4444",
    "default_website": "https://www.mohinhkientruc.org"
}

# 🗺️ BẢNG ÁNH XẠ CHỦ ĐỀ VÀ LINK BÀI VIẾT CHUYÊN SÂU TRÊN WEBSITE
TOPIC_LANDING_PAGES = [
    (["quy hoạch", "đô thị", "phân khu", "bản đồ quy hoạch"], "https://www.mohinhkientruc.org/mo-hinh-quy-hoach/"),
    (["nhà máy", "nhà xưởng", "khu công nghiệp", "kcn", "logistics"], "https://www.mohinhkientruc.org/mo-hinh-nha-may/"),
    (["trường học", "rmit", "uts", "đại học", "giáo dục"], "https://www.mohinhkientruc.org/lam-sa-ban-truong-hoc/"),
    (["tod", "metro", "tuyến metro", "nhà ga"], "https://www.mohinhkientruc.org/mo-hinh-tod-sa-ban/"),
    (["sửa chữa", "bảo dưỡng", "phục hồi", "nâng cấp led", "thay đèn"], "https://www.mohinhkientruc.org/sua-chua-mo-hinh-kien-truc/"),
    (["thủy sản", "hồ nuôi", "triển lãm", "báo giá", "chung cư", "cao tầng", "kiến trúc"], "https://www.mohinhkientruc.org/mo-hinh-kien-truc/")
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
    """
    Trích xuất link landing page phù hợp nhất theo chỉ đạo của Sếp Tiến:
    1. Ưu tiên 1: Link bài viết cụ thể từ cột Rollup 'Link mohinhkientruc.org' trên Notion.
    2. Ưu tiên 2: Tự động phân tích từ khóa chủ đề bài viết để trỏ đúng URL bài viết chuyên sâu.
    3. Ưu tiên 3: Trang Báo giá & Dịch vụ cốt lõi /mo-hinh-kien-truc/.
    """
    if rollup_url and rollup_url.startswith("http"):
        print(f"🔗 [NOTION ROLLUP LINK]: Trỏ chính xác bài viết Notion: {rollup_url}")
        return rollup_url

    search_text = (title + " " + content).lower()
    for keywords, target_url in TOPIC_LANDING_PAGES:
        for kw in keywords:
            if kw in search_text:
                print(f"🎯 [CHỦ ĐỀ KHỚP TỪ KHÓA '{kw}']: Trỏ về bài viết chuyên sâu: {target_url}")
                return target_url

    print("🌐 [FALLBACK]: Trỏ về Trang Báo Giá Cốt Lõi: https://www.mohinhkientruc.org/mo-hinh-kien-truc/")
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

        # Fallbacks
        if not spin_text:
            fb_objs = props.get("Spin - Fanpage FB", {}).get("rich_text", [])
            spin_text = "".join([t.get("plain_text", "") for t in fb_objs]).strip()
        if not spin_text:
            orig_objs = props.get("Nội dung gốc", {}).get("rich_text", [])
            spin_text = "".join([t.get("plain_text", "") for t in orig_objs]).strip()

        # Media
        img_files = props.get("Hình ảnh", {}).get("files", [])
        img_urls = [f.get("file", {}).get("url") or f.get("external", {}).get("url") for f in img_files]

        vid_files = props.get("Video", {}).get("files", [])
        vid_urls = [f.get("file", {}).get("url") or f.get("external", {}).get("url") for f in vid_files]

        yt_url = props.get("Link Video YouTube Channel", {}).get("url")

        # Rollup URL
        rollup_url = None
        rollup_prop = props.get("Link mohinhkientruc.org", {})
        if rollup_prop.get("type") == "rollup":
            arr = rollup_prop.get("rollup", {}).get("array", [])
            for item in arr:
                if item.get("type") == "url":
                    rollup_url = item.get("url")
                    break

        # Dynamic smart landing page
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
    """
    Áp dụng Quy tắc Media & Nút CTA chuẩn:
    - CTA 'Tìm hiểu thêm' trỏ đúng Link bài viết theo chủ đề nội dung (Dynamic Contextual Landing Page).
    - 100% Không dùng nút 'Gọi ngay' cho kênh Mô hình.
    """
    has_img = len(post_data.get("img_urls", [])) > 0
    has_vid = len(post_data.get("vid_urls", [])) > 0
    has_yt = bool(post_data.get("yt_url"))

    local_media_path = None
    cta_option = "Tìm hiểu thêm"
    cta_url = post_data.get("website_link")

    print("\n--- PHÂN TÍCH QUY TẮC MEDIA & NÚT CTA CHỦ ĐỀ THỰC TẾ ---")
    if has_img and has_yt:
        print("📌 [QUY TẮC 4]: Có cả Ảnh và Link YouTube -> Ưu tiên tải ảnh, CTA 'Tìm hiểu thêm' (Random Link Bài Viết / Video YouTube).")
        local_media_path = download_media_file(post_data["img_urls"][0], "img")
        choice = random.choice(["website", "youtube"])
        if choice == "website":
            cta_url = post_data.get("website_link")
        else:
            cta_url = post_data["yt_url"]

    elif has_img:
        print(f"📌 [QUY TẮC 1]: Có ảnh sản phẩm -> Tải ảnh lên GBP, CTA 'Tìm hiểu thêm' trỏ bài viết chuyên sâu: {cta_url}")
        local_media_path = download_media_file(post_data["img_urls"][0], "img")

    elif has_vid and not has_img:
        print(f"📌 [QUY TẮC 2]: Có video (không ảnh) -> Tải video lên GBP, CTA 'Tìm hiểu thêm' trỏ bài viết: {cta_url}")
        local_media_path = download_media_file(post_data["vid_urls"][0], "vid")

    elif has_yt and not has_img and not has_vid:
        print("📌 [QUY TẮC 3]: Video YouTube đơn lẻ -> CTA 'Tìm hiểu thêm' trỏ về YouTube Link.")
        cta_url = post_data["yt_url"]

    else:
        print("📌 [DỰ PHÒNG]: Dùng ảnh sa bàn mặc định chất lượng cao, CTA 'Tìm hiểu thêm' trỏ bài viết tương ứng.")

    print(f"➡️ Media đính kèm: {local_media_path}")
    print(f"➡️ Nút CTA: '{cta_option}' | URL Đích: {cta_url}")
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
        print(f"⬇️ Đang tải media từ: {download_url}")
        req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp, open(save_path, 'wb') as f:
            f.write(resp.read())
        print(f"✅ Tải media thành công ({os.path.getsize(save_path)/1024:.1f} KB): {save_path}")
        return save_path
    except Exception as e:
        print(f"⚠️ Lỗi tải media ({e}), bỏ qua đính kèm file.")
        return None

def publish_to_gbp(content_text, media_path=None, cta_option="Tìm hiểu thêm", cta_url=None):
    """Thực thi đăng bài trực tiếp lên Google Business Profile qua Selenium"""
    print("\n[2] Khởi chạy Selenium Chrome Profile để đăng bài GBP...")
    options = Options()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    post_link = GBP_LOCATION["profile_url"]

    try:
        driver.get(GBP_LOCATION["url"])
        time.sleep(6)

        # 1. Click 'Thêm bài đăng'
        plus_btn = None
        btns = driver.find_elements(By.XPATH, "//*[contains(text(), 'Thêm bài đăng') or contains(text(), 'Thêm nội dung cập nhật')]")
        for b in btns:
            if b.is_displayed():
                plus_btn = b
                break

        if plus_btn:
            driver.execute_script("arguments[0].click();", plus_btn)
            time.sleep(4)

        # 2. Điền nội dung văn bản
        textarea = None
        for attempt in range(5):
            tas = driver.find_elements(By.XPATH, "//textarea")
            for ta in tas:
                if ta.is_displayed():
                    textarea = ta
                    break
            if textarea:
                break
            time.sleep(1)

        if textarea:
            driver.execute_script(SET_REACT_TEXTAREA_JS, textarea, content_text[:1450])
            print("✅ Đã điền nội dung bài viết B2B vào khung soạn thảo GBP!")
            time.sleep(2)

        # 3. Tải Media (Ảnh/Video)
        if media_path and os.path.exists(media_path):
            try:
                file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                if file_inputs:
                    file_inputs[0].send_keys(media_path)
                    print(f"✅ Đã tải file media lên: {os.path.basename(media_path)}")
                    time.sleep(5)
            except Exception as e:
                print(f"⚠️ Cảnh báo tải media: {e}")

        # 4. Thêm Nút CTA ('Tìm hiểu thêm' trỏ link chuyên sâu)
        try:
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
            print(f"✅ Đã chọn Nút CTA: '{cta_option}'")
            time.sleep(2)

            if cta_url:
                inps = driver.find_elements(By.XPATH, "//input[@type='text' or @type='url' or not(@type)]")
                for inp in reversed(inps):
                    if inp.is_displayed() and inp.tag_name == 'input' and inp.get_attribute("type") != "file":
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
                        inp.click()
                        time.sleep(0.5)
                        inp.clear()
                        inp.send_keys(cta_url)
                        time.sleep(0.5)
                        inp.send_keys(Keys.TAB)
                        print(f"✅ Đã nhập link CTA bài viết đích: {cta_url}")
                        time.sleep(2)
                        break
        except Exception as e:
            print(f"⚠️ Cảnh báo cấu hình CTA: {e}")

        # 5. Bấm Đăng bài
        submit_btns = driver.find_elements(By.XPATH, "//button[contains(., 'Bài đăng') or contains(., 'Đăng')]")
        for sb in submit_btns:
            if sb.is_displayed() and sb.tag_name == 'button':
                driver.execute_script("arguments[0].click();", sb)
                print("🎉 ĐÃ BẤM NÚT XUẤT BẢN THÀNH CÔNG!")
                time.sleep(6)
                break

        # 6. Đóng popup sau xuất bản
        bo_qua_btns = driver.find_elements(By.XPATH, "//*[contains(text(), 'Bỏ qua') or contains(text(), 'Xong')]")
        for bq in bo_qua_btns:
            if bq.is_displayed():
                driver.execute_script("arguments[0].click();", bq)
                time.sleep(2)
                break

        return True, post_link

    except Exception as e:
        print(f"❌ Lỗi trong quá trình thao tác GBP: {e}")
        return False, None
    finally:
        driver.quit()

def update_notion_published_status(page_id, post_link):
    """Cập nhật Link GBP và Ngày đăng vào Notion DB 'BẢNG CONTENT'"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"\n[3] Đang cập nhật Notion Page {page_id} với Link: {post_link} và Ngày: {today_str}...")

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
    if res.status_code == 200:
        print("✅ Đã cập nhật thành công BẢNG CONTENT trên Notion!")
        return True
    else:
        print(f"❌ Lỗi cập nhật Notion: {res.status_code} - {res.text}")
        return False

def record_activity_log(post_title, post_link):
    """Ghi nhận vào Notion Database 'NHẬT KÝ THAO TÁC MARKETING SONG ANH'"""
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"\n[4] Ghi nhận Activity Log vào Notion DB '{ACTIVITY_LOG_DB_ID}'...")

    body = {
        "parent": {"database_id": ACTIVITY_LOG_DB_ID},
        "properties": {
            "Hành Động": {
                "title": [{"text": {"content": f"Đăng bài GBP: [{post_title[:60]}]"}}]
            },
            "Thời Gian": {
                "rich_text": [{"text": {"content": now_str}}]
            },
            "Phân Hệ": {
                "select": {"name": "GBP"}
            },
            "Mô Tả Ngắn": {
                "rich_text": [{"text": {"content": f"Đã tự động xuất bản bài viết lên GBP Dịch vụ làm mô hình kiến trúc Song Anh (Thủ Đức). CTA 'Tìm hiểu thêm' trỏ link bài viết phù hợp. Link: {post_link}"}}]
            },
            "Người Thực Hiện": {
                "rich_text": [{"text": {"content": "Kiến - Trợ lý Lập Trình"}}]
            },
            "Trạng Thái": {
                "select": {"name": "Hoàn Thành"}
            }
        }
    }

    res = requests.post("https://api.notion.com/v1/pages", headers=NOTION_HEADERS, json=body)
    if res.status_code == 200:
        print("✅ Đã ghi nhận Activity Log thành công!")
    else:
        print(f"⚠️ Không thể ghi Activity Log: {res.status_code}")

def main():
    print("="*80)
    print("🚀 TOOL AUTOMATION ĐĂNG BÀI GOOGLE BUSINESS PROFILE (GBP) SONG ANH 🚀")
    print("🌐 CHẾ ĐỘ: Dynamic Landing Page trỏ đúng bài viết chuyên sâu theo chủ đề")
    print("="*80)

    post = fetch_candidate_post_from_notion()
    if not post:
        print("[-] Kết thúc: Không có bài viết nào cần xuất bản.")
        return

    media_path, cta_option, cta_url = resolve_media_and_cta_rules(post)
    success, post_link = publish_to_gbp(post["content"], media_path, cta_option, cta_url)

    if success:
        update_notion_published_status(post["page_id"], post_link)
        record_activity_log(post["title"], post_link)
        print("\n" + "="*80)
        print("🎉🎉🎉 XUẤT BẢN BÀI ĐĂNG GBP VÀ ĐỒNG BỘ TOÀN BỘ HỆ THỐNG 100% THÀNH CÔNG! 🎉🎉🎉")
        print("="*80)
    else:
        print("\n❌ Quá trình đăng bài GBP chưa thành công, vui lòng kiểm tra lại trạng thái trình duyệt.")

if __name__ == "__main__":
    main()
