# -*- coding: utf-8 -*-
"""
Tool: fb_remote_recomment_engine.py (v3.1 - Mobile Command Autonomous Engine)
Mục đích: Tự động hóa Re-comment tương tác bài viết Facebook phục vụ Sếp Tiến điều khiển từ xa qua điện thoại (Antigravity).

🌟 TÍNH NĂNG ĐẶC BIỆT CHO ĐIỀU KHIỂN TỪ ĐIỆN THOẠI:
1. DUAL-LAUNCH ENGINE:
   - Nếu Chrome Port 9222 đang mở -> Tự động kết nối.
   - Nếu Chrome chưa mở (Sếp đang đi ngoài đường) -> Tự động khởi chạy Chrome Profile độc lập, thực thi xong tự đóng!
2. CHỤP ẢNH BẰNG CHỨNG (PROOF SCREENSHOT):
   - Tự động lưu ảnh chụp màn hình sau khi bình luận để báo cáo trực quan cho Sếp xem ngay trên điện thoại.
3. ANTI-SPAM & ANTI-CHECKPOINT SHIELD:
   - Gõ phím Human Typing, delay ngẫu nhiên, cuộn trang đọc bài tự nhiên.
4. ACTOR VOICE SWITCHER:
   - 'fanpage_song_anh' -> Fanpage Mô hình kiến trúc Song Anh
   - 'profile' -> Profile cá nhân Song Anh
   - 'fanpage_org' -> Fanpage Architectural Model Org
"""

import os
import sys
import io
import time
import json
import random
import argparse
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 🎯 CẤU HÌNH ĐƯỜNG DẪN & NOTION
PROFILE_DIR = r"D:\Song_Anh\_Shared_Core\Credentials\facebook_chrome_profile"
SCREENSHOT_DIR = r"C:\Users\Aer\.gemini\antigravity\brain\c48a7cb3-192c-4e18-b380-1f993c5a3dad"

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "ntn_" + "202316998566adC5moVwLDu5vZcjHFYLKdcPcvKO1mq1uE")
NOTION_VERSION = "2022-06-28"
CONTENT_DB_ID = "33d4b5e73d90809faebfd11a9a8b0c0e"
ACTIVITY_LOG_DB_ID = "3c24b5e73d9081b4b505f85f9c9bfcae"

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

RE_CMT_SPIN_TEMPLATES = [
    "Mô hình kiến trúc Song Anh chuyên thi công sa bàn dự án B2B trọn gói: Sa bàn quy hoạch KCN & Đô thị, Sa bàn cao tầng chung cư, Sa bàn nhà máy kho xưởng. Hotline tư vấn & báo giá: 0929 22 4444 - Website: https://mohinhkientruc.org",
    "Quý Chủ đầu tư, Đơn vị thiết kế & Ban QLDA cần tư vấn phương án kỹ thuật sa bàn kiến trúc (tỷ lệ 1/500, 1/1000, vật liệu Acrylic, hệ thống LED phân tầng thông minh), vui lòng liên hệ Xưởng Song Anh: 0929 22 4444 (Zalo Song Anh).",
    "Mô hình Song Anh cung cấp 6 dịch vụ cốt lõi: 1) Sa bàn quy hoạch đô thị; 2) Sa bàn cao tầng; 3) Sa bàn nhà máy kho xưởng; 4) Sa bàn biệt thự nhà phố; 5) Sa bàn cắt bổ nội thất 3D; 6) Bảo trì & sửa chữa sa bàn tận nơi toàn quốc. Hotline: 0929 22 4444.",
    "Hình ảnh thực tế sa bàn chế tác trực tiếp tại Xưởng Mô hình Song Anh (TP. Thủ Đức, TP.HCM). Hỗ trợ đo đạc, lên bản vẽ 3D và bàn giao lắp đặt tận nơi trên toàn quốc. Chi tiết tại: https://mohinhkientruc.org"
]

VOICE_NAMES = {
    "profile": "Profile Song Anh",
    "fanpage_song_anh": "Fanpage Mô hình kiến trúc Song Anh",
    "fanpage_org": "Fanpage Architectural Model Org"
}

def is_port_9222_open():
    try:
        r = requests.get("http://localhost:9222/json/version", timeout=1.5)
        return r.status_code == 200
    except Exception:
        return False

def human_typing(driver, element, text):
    """Gõ phím mô phỏng người thật với độ trễ ngẫu nhiên 20ms - 75ms"""
    element.click()
    time.sleep(0.5)
    for char in text:
        element.send_keys(char)
        delay = random.uniform(0.02, 0.075)
        if char in [',', '.', ':', ' ', '\n']:
            delay += random.uniform(0.1, 0.25)
        time.sleep(delay)

def switch_actor_voice_if_needed(driver, target_voice="fanpage_song_anh"):
    """Tự động chuyển đổi tư cách bình luận (Voice Switcher)"""
    print(f"🔄 Đồng bộ Tư cách bình luận: [{VOICE_NAMES.get(target_voice, target_voice)}]")
    try:
        switch_btns = driver.find_elements(By.XPATH, "//div[@aria-label='Bình luận với tư cách' or @aria-label='Comment as' or contains(@aria-label, 'tư cách')]")
        if switch_btns and switch_btns[0].is_displayed():
            driver.execute_script("arguments[0].click();", switch_btns[0])
            time.sleep(2)
            target_text = "Mô hình kiến trúc Song Anh" if "fanpage" in target_voice else "Song Anh"
            items = driver.find_elements(By.XPATH, f"//div[@role='menuitem' or @role='radio' or @role='button'][contains(., '{target_text}')]")
            if items:
                driver.execute_script("arguments[0].click();", items[0])
                print(f"✅ Đã chọn tư cách: {target_text}")
                time.sleep(2)
    except Exception as e:
        print(f"ℹ️ Tư cách mặc định của phiên: {e}")

def create_driver():
    """Tự động tạo driver qua Port 9222 hoặc mở Profile độc lập"""
    options = Options()
    if is_port_9222_open():
        print("🔗 Phát hiện Chrome Port 9222 đang mở -> Kết nối trực tiếp!")
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=options)
        should_quit = False
    else:
        print("🚀 Khởi chạy Chrome Profile chuyên dụng độc lập...")
        os.makedirs(PROFILE_DIR, exist_ok=True)
        options.add_argument(f"--user-data-dir={PROFILE_DIR}")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=options)
        should_quit = True
    return driver, should_quit

def execute_recomment(post_url, custom_text=None, target_voice="fanpage_song_anh"):
    """Thực thi Re-comment hoàn chỉnh và chụp ảnh bằng chứng"""
    driver, should_quit = create_driver()
    proof_path = os.path.join(SCREENSHOT_DIR, "fb_recomment_proof.png")

    try:
        print(f"🌐 Điều hướng đến bài viết: {post_url}")
        driver.get(post_url)
        time.sleep(random.uniform(5.0, 7.0))

        # Đóng popup che
        try:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
        except Exception:
            pass

        # Warm-up scroll
        print("📜 Cuộn trang tự nhiên...")
        driver.execute_script("window.scrollBy(0, 400);")
        time.sleep(random.uniform(2.0, 3.5))

        # Switch Voice
        switch_actor_voice_if_needed(driver, target_voice)

        # Tìm ô bình luận
        comment_box = None
        selectors = [
            'div[aria-label="Viết bình luận"]',
            'div[aria-label="Write a comment"]',
            'div[aria-label="Viết câu trả lời..."]',
            'div[contenteditable="true"][role="textbox"]',
            'form div[role="textbox"]'
        ]

        for sel in selectors:
            try:
                elems = driver.find_elements(By.CSS_SELECTOR, sel)
                for elem in elems:
                    if elem.is_displayed():
                        comment_box = elem
                        break
                if comment_box:
                    break
            except Exception:
                pass

        if not comment_box:
            print("❌ Không tìm thấy ô bình luận hiển thị.")
            driver.save_screenshot(proof_path)
            return False, proof_path

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", comment_box)
        time.sleep(1.5)

        # Gõ văn bản
        content = custom_text if custom_text else random.choice(RE_CMT_SPIN_TEMPLATES)
        print(f"✍️ Đang gõ Re-comment ({len(content)} ký tự)...")
        driver.execute_script("arguments[0].focus();", comment_box)
        comment_box.click()
        time.sleep(1)

        human_typing(driver, comment_box, content)
        time.sleep(random.uniform(2.0, 3.5))

        # Gửi
        print("🚀 Nhấn Enter gửi bình luận...")
        comment_box.send_keys(Keys.RETURN)
        time.sleep(random.uniform(5.0, 6.5))

        # Chụp ảnh bằng chứng
        driver.save_screenshot(proof_path)
        print(f"📸 Đã chụp ảnh bằng chứng nghiệm thu: {proof_path}")
        print("🎉 RE-COMMENT HOÀN TẤT THÀNH CÔNG 100%!")
        return True, proof_path

    except Exception as e:
        print(f"❌ Lỗi: {e}")
        try:
            driver.save_screenshot(proof_path)
        except Exception:
            pass
        return False, proof_path
    finally:
        if should_quit:
            driver.quit()

def fetch_posts_from_notion():
    """Lấy danh sách bài viết Fanpage trên Notion"""
    body = {
        "filter": {
            "property": "Link Fanpage",
            "url": {
                "is_not_empty": True
            }
        },
        "page_size": 10
    }
    try:
        res = requests.post(f"https://api.notion.com/v1/databases/{CONTENT_DB_ID}/query", headers=NOTION_HEADERS, json=body)
        if res.status_code == 200:
            pages = res.json().get("results", [])
            items = []
            for p in pages:
                props = p["properties"]
                title_objs = props.get("Tiêu đề bài viết", {}).get("title", [])
                title = "".join([t.get("plain_text", "") for t in title_objs]).strip()
                fb_url = props.get("Link Fanpage", {}).get("url")
                if fb_url and "facebook.com" in fb_url:
                    items.append({
                        "page_id": p["id"],
                        "title": title,
                        "url": fb_url
                    })
            return items
    except Exception as e:
        print(f"⚠️ Lỗi đọc Notion: {e}")
    return []

def log_activity(task_name, desc):
    """Ghi nhật ký vào Notion"""
    try:
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        body = {
            "parent": {"database_id": ACTIVITY_LOG_DB_ID},
            "properties": {
                "Hành Động": {"title": [{"text": {"content": task_name}}]},
                "Thời Gian": {"rich_text": [{"text": {"content": now_str}}]},
                "Phân Hệ": {"select": {"name": "Facebook"}},
                "Mô Tả Ngắn": {"rich_text": [{"text": {"content": desc}}]},
                "Người Thực Hiện": {"rich_text": [{"text": {"content": "Kiến - Trợ lý Lập Trình"}}]},
                "Trạng Thái": {"select": {"name": "Hoàn Thành"}}
            }
        }
        requests.post("https://api.notion.com/v1/pages", headers=NOTION_HEADERS, json=body)
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(description="Facebook Autonomous Engine v3.1")
    parser.add_argument("--url", help="URL bài viết Facebook", default=None)
    parser.add_argument("--text", help="Nội dung bình luận tùy chỉnh", default=None)
    parser.add_argument("--voice", choices=["profile", "fanpage_song_anh", "fanpage_org"], default="fanpage_song_anh")
    parser.add_argument("--from-notion", action="store_true", help="Lấy từ Notion DB")

    args = parser.parse_args()

    if args.from_notion:
        posts = fetch_posts_from_notion()
        if posts:
            p = posts[0]
            success, proof = execute_recomment(p["url"], args.text, args.voice)
            if success:
                log_activity(f"Re-Comment FB: [{p['title'][:35]}...]", f"Đã Re-comment bài viết {p['url']} với tư cách {VOICE_NAMES.get(args.voice, args.voice)}")
        else:
            print("[-] Không có bài viết nào trên Notion.")
    elif args.url:
        success, proof = execute_recomment(args.url, args.text, args.voice)
        if success:
            log_activity("Re-Comment FB Tùy Chọn", f"Đã Re-comment {args.url} với tư cách {VOICE_NAMES.get(args.voice, args.voice)}")
    else:
        default_url = "https://www.facebook.com/congtymohinhkientruc/posts/pfbid02iw9AFXgWbBadGXHW6c4zNzUUco12KJSEeuWAXTSjWmhspjBeY7HDuthx2TSrdMRwl"
        success, proof = execute_recomment(default_url, args.text, args.voice)
        if success:
            log_activity("Re-Comment FB Test", f"Đã Re-comment bài mẫu {default_url}")

if __name__ == "__main__":
    main()
