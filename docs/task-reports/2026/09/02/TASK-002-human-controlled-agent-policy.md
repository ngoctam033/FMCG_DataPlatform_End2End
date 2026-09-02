# TASK-002 — Thiết lập chính sách kiểm soát agent

## Thông tin

- Ngày thực hiện: 2026-09-02
- Trạng thái: Completed
- Người thực hiện: Codex
- Task/Issue: Tạo `AGENTS.md` với chính sách human-controlled implementation

## Mục tiêu

Thiết lập ranh giới rõ ràng để agent hỗ trợ phân tích và đề xuất nhưng không tự ý thay đổi production code hoặc trạng thái hệ thống.

## Thay đổi đã thực hiện

- Tạo `AGENTS.md` tại root của repository.
- Quy định các loại thay đổi agent được phép và không được phép thực hiện.
- Quy định quy trình đề xuất thay đổi code để chủ dự án tự áp dụng.
- Quy định quyền đọc, kiểm tra và điều kiện tạo test.
- Bổ sung cơ chế ngoại lệ theo phạm vi cụ thể của từng task.
- Bổ sung ma trận quyền theo khu vực repository và quy tắc placeholder.

## Files changed

- `AGENTS.md`
- `docs/task-reports/2026/09/02/TASK-002-human-controlled-agent-policy.md`

## Quyết định kỹ thuật

- Human-controlled implementation là chính sách mặc định áp dụng cho mọi agent.
- Quyền sửa production code chỉ có hiệu lực khi người dùng cấp phép rõ ràng cho đúng task và phạm vi file.
- Yêu cầu sửa lỗi chung không được xem là quyền tự động sửa production code.

## Kiểm thử

- [ ] Static checks hoặc lint — không áp dụng vì chỉ thay đổi tài liệu.
- [ ] Unit tests — không áp dụng vì chỉ thay đổi tài liệu.
- [ ] Integration tests — không áp dụng vì chỉ thay đổi tài liệu.
- [x] Kiểm tra thủ công nội dung Markdown và phạm vi chính sách.

## Kết quả

Repository đã có chính sách bắt buộc giúp ngăn agent tự ý chèn code chưa được chủ dự án kiểm duyệt.

## Hạn chế và công việc tiếp theo

- Cần bổ sung project context, repository workflow và Definition of Done vào `AGENTS.md` trong task riêng.
- Cần thiết kế skill `change-proposal` để chuẩn hóa chất lượng các đề xuất thay đổi.

