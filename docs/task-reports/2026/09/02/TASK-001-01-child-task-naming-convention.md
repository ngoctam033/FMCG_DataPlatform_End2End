# TASK-001-01 — Bổ sung quy ước đặt tên task con

## Thông tin

- Ngày thực hiện: 2026-09-02
- Trạng thái: Completed
- Người thực hiện: Codex
- Parent task: TASK-001
- Task/Issue: Bổ sung quan hệ task cha–con vào quy ước Task Report

## Mục tiêu

Mở rộng quy ước task ID để tên task và file báo cáo thể hiện rõ quan hệ giữa task cha và task con.

## Thay đổi đã thực hiện

- Bổ sung định dạng mã task phân cấp.
- Quy định cách cấp số task gốc và task con.
- Giới hạn task ở tối đa hai cấp con.
- Quy định trạng thái hoàn thành và không tái sử dụng task ID.
- Bổ sung trường `Parent task` vào template báo cáo.

## Files changed

- `docs/task-reports/README.md`
- `docs/task-reports/templates/task-report-template.md`
- `docs/task-reports/2026/09/02/TASK-001-01-child-task-naming-convention.md`

## Quyết định kỹ thuật

- Sử dụng định dạng `TASK-NNN-NN-NN` thay vì thư mục lồng theo task để quan hệ cha–con vẫn hiển thị khi tìm kiếm và sắp xếp tên file.
- Giới hạn hai cấp con nhằm giữ cấu trúc task dễ đọc và quản lý.

## Kiểm thử

- [ ] Static checks hoặc lint — không áp dụng vì chỉ thay đổi tài liệu.
- [ ] Unit tests — không áp dụng vì chỉ thay đổi tài liệu.
- [ ] Integration tests — không áp dụng vì chỉ thay đổi tài liệu.
- [x] Kiểm tra thủ công định dạng, ví dụ và quan hệ task cha–con.

## Kết quả

Tài liệu và template hiện hỗ trợ thống nhất task gốc, task con cấp 1 và task con cấp 2.

## Hạn chế và công việc tiếp theo

- Chưa có automation phát hiện task ID trùng hoặc sai định dạng.

