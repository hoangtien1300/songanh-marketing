# 📘 HƯỚNG DẪN 3 BƯỚC LẤY META PAGE ACCESS TOKEN
**Dành cho Sếp Phạm Hoàng Tiến - Song Anh Group**
*Hệ thống AI Marketing Suite & Meta Graph API Engine v19.0*

---

### 🔹 BƯỚC 1: Mở Công Cụ Meta Graph API Explorer & Chọn Fanpage
1. Truy cập đường dẫn Meta Graph API Explorer chính thức:  
   👉 **[https://developers.facebook.com/tools/explorer/](https://developers.facebook.com/tools/explorer/)**
2. Tại giao diện điều khiển góc phải màn hình:
   - **Meta App**: Chọn App Facebook của Song Anh (hoặc App mặc định).
   - **User or Page**: Nhấp vào menu thả xuống và chọn **Get Page Access Token** (Lấy Access Token của Trang).
   - Chọn đúng Fanpage: **Fanpage Mô hình kiến trúc Song Anh** (Page ID: `100063928172930`).

---

### 🔹 BƯỚC 2: Thêm Quyền Truy Cập (Permissions) & Tạo Token
1. Trong mục **Permissions** (Quyền) ở cột bên phải, bấm **Add a Permission** và tìm/thêm 3 quyền quan trọng sau:
   - `pages_read_engagement` (Đọc chỉ số tương tác bài viết)
   - `pages_show_list` (Hiển thị danh sách Fanpage quản lý)
   - `read_insights` (Đọc số liệu Analytics & Insights thực tế)
2. Nhấn nút màu xanh **Generate Access Token** (Tạo Mã Truy Cập).
3. Xác nhận phân quyền trên cửa sổ pop-up của Facebook.

---

### 🔹 BƯỚC 3: Dán Token vào Tệp `facebook_credentials.json`
1. Sao chép (Copy) chuỗi mã Token dài vừa xuất hiện ở ô **Access Token**.
2. Mở tệp khai báo thông tin credentials tại máy tính:  
   📂 `d:\Song_Anh\marketing_workflow_app\facebook_credentials.json`
3. Dán mã Token vào trường `"page_access_token"`:

```json
{
  "app_id": "VÍ_DỤ_APP_ID",
  "app_secret": "VÍ_DỤ_APP_SECRET",
  "page_id": "100063928172930",
  "page_access_token": "DÁN_CHOI_PAGE_ACCESS_TOKEN_VÀO_ĐÂY",
  "user_access_token": "",
  "updated_at": "2026-08-20 09:00:00"
}
```
4. Lưu tệp `facebook_credentials.json`. Hệ thống `fb_page_insights_extractor.py` sẽ tự động kết nối Meta Graph API v19.0 bóc tách 100% số liệu thực tế!

---
*Ghi chú: Token tạo từ Explorer là token ngắn hạn (1-2 giờ). Để lấy Long-lived Token (60 ngày), Sếp Tiến có thể dùng công cụ Access Token Tool hoặc nhấn 'Access Token Info' -> 'Open in Access Token Tool' -> 'Extend Access Token'.*
