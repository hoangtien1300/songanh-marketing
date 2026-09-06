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
