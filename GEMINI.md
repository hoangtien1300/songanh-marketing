# 🏢 SONG ANH MARKETING - WORKSPACE RULES

## 🎨 QUY TẮC BỐ CỤC GIAO DIỆN WEBAPP & DASHBOARD (UI LAYOUT INVARIANTS)

Khi xây dựng, sửa đổi hoặc mở rộng bất kỳ giao diện, trang, hoặc module mới (.module-panel) trong hệ thống WebApp / Dashboard:

1. **Tiêu đề mục (Module Header / Banner)**:
   - **Bắt buộc luôn nằm ở vị trí đầu tiên trên cùng** của container module (.module-panel).
   - Nằm ngay dưới Topbar điều hướng. Chứa biểu tượng icon, tiêu đề chính <h2> / <h1>, mô tả phạm vi nội dung và badge trạng thái.

2. **Chân trang toàn cục (<footer>)**:
   - **Bắt buộc luôn nằm ở vị trí cuối cùng bên dưới tất cả các module panels** (.module-panel) trong thẻ <main>.
   - **Tuyệt đối KHÔNG chèn thẻ module mới sau thẻ <footer> trong cấu trúc DOM**, tránh tình trạng Footer trôi lên hiển thị đè lên trên tiêu đề hoặc nội dung của module.

3. **Các thành phần Modal / Dialog / Overlay (.modal)**:
   - Đặt tách biệt ở cuối thẻ <main> hoặc trước thẻ đóng </body>, đảm bảo không làm gãy luồng hiển thị tự nhiên của các module panels và footer.

4. **Quy chuẩn thích ứng Responsive Mobile & Tablet (Mobile-First Safe Area)**:
   - **Đồng bộ và thích ứng với tablet và mobile**: Khi cập nhật bất kỳ tính năng, module, hoặc thành phần nào, bắt buộc phải kiểm tra và tối ưu hiển thị hoàn hảo trên cả màn hình Mobile (< 640px) và Tablet (640px - 1024px).
   - **Khoảng đệm an toàn dưới cùng (Safe Area Bottom Padding)**: Container nội dung chính (`<main>`) bắt buộc luôn có class padding bottom cho mobile (`pb-28 lg:pb-8`) nhằm đảm bảo thanh điều hướng dưới cùng (`#mobile-bottom-nav`) không bao giờ che khuất nội dung dưới đáy hoặc Footer.
   - **Hiển thị dữ liệu bảng thích ứng (Responsive Data Tables)**: Các bảng dữ liệu nhiều cột không được để tràn ngang khó xem trên điện thoại. Bắt buộc chuyển đổi linh hoạt: hiển thị dạng Card List gọn gàng trên màn hình nhỏ (< 640px) và Table chuyên nghiệp trên màn hình lớn (>= 640px).
   - **Điều khiển và Bộ lọc (Filter / Search Controls)**: Các thanh tìm kiếm, bộ lọc, nút bấm phải hỗ trợ `flex-wrap`, co giãn linh hoạt (`w-full sm:w-auto`), touch target đủ lớn (>= 40px) để thao tác bằng một tay trên điện thoại mượt mà.
