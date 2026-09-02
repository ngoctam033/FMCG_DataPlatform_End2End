# TASK-001 — Thiết lập cấu trúc task report

## Thông tin

- Ngày thực hiện: 2026-09-02
- Trạng thái: Completed
- Người thực hiện: Codex
- Task/Issue: Thiết lập nơi lưu báo cáo của từng task theo ngày

## Mục tiêu

Tạo cấu trúc thống nhất để mỗi task có một báo cáo Markdown được lưu và tra cứu theo ngày thực hiện.

## Thay đổi đã thực hiện

- Tạo khu vực `docs/task-reports/`.
- Phân cấp báo cáo theo cấu trúc `YYYY/MM/DD`.
- Thêm quy ước đặt tên và quy trình tạo báo cáo.
- Thêm template báo cáo dùng chung.
- Cập nhật tài liệu tổng quan để phản ánh cấu trúc mới.

## Files changed

- `README.md`
- `docs/README.md`
- `docs/task-reports/README.md`
- `docs/task-reports/templates/task-report-template.md`
- `docs/task-reports/2026/09/02/TASK-001-task-report-structure.md`

## Quyết định kỹ thuật

- Sử dụng cây thư mục `YYYY/MM/DD` để báo cáo được sắp xếp tự nhiên và không tập trung quá nhiều file tại một cấp.
- Sử dụng task ID làm định danh chính thay vì commit hash để tránh vấn đề hash tự tham chiếu.

## Kiểm thử

- [ ] Static checks hoặc lint — không áp dụng vì chỉ thay đổi tài liệu.
- [ ] Unit tests — không áp dụng vì chỉ thay đổi tài liệu.
- [ ] Integration tests — không áp dụng vì chỉ thay đổi tài liệu.
- [x] Kiểm tra thủ công cấu trúc thư mục, đường dẫn và nội dung Markdown.

## Kết quả

Dự án đã có nơi lưu trữ và template chuẩn cho báo cáo của từng task theo ngày.

## Hạn chế và công việc tiếp theo

- Chưa có automation kiểm tra mỗi commit hoặc pull request đã kèm task report.
- Cần xác định quy tắc cấp số task khi xây dựng project rules.

