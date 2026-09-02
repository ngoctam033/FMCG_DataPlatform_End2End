# Task reports

Mỗi task hoàn thành cần có một báo cáo Markdown đi kèm với commit chứa thay đổi của task đó.

## Cấu trúc lưu trữ

Báo cáo được phân cấp theo ngày thực hiện:

```text
task-reports/
├── README.md
├── templates/
│   └── task-report-template.md
└── YYYY/
    └── MM/
        └── DD/
            ├── TASK-NNN-short-description.md
            └── TASK-NNN-NN-short-description.md
```

Ví dụ:

```text
docs/task-reports/2026/09/02/TASK-001-codebase-bootstrap.md
docs/task-reports/2026/09/02/TASK-001-01-create-report-template.md
```

## Quy ước mã task

Task ID thể hiện quan hệ cha–con bằng cách thêm một nhóm hai chữ số cho mỗi cấp con:

```text
TASK-001             # Task gốc
TASK-001-01          # Task con cấp 1 của TASK-001
TASK-001-02          # Task con cấp 1 tiếp theo của TASK-001
TASK-001-02-01       # Task con cấp 2 của TASK-001-02
```

Áp dụng các quy tắc sau:

- Task gốc dùng định dạng `TASK-NNN`, với `NNN` là số thứ tự gồm ba chữ số.
- Mỗi cấp con thêm một nhóm `-NN`, với `NN` là số thứ tự gồm hai chữ số trong phạm vi task cha.
- Task ID phải duy nhất trong toàn bộ dự án và không được tái sử dụng, kể cả khi task bị hủy.
- Task độc lập mới tăng số của task gốc; task con chỉ tăng số trong phạm vi task cha.
- Giới hạn tối đa hai cấp con: `TASK-NNN-NN-NN`.
- Task cha chỉ được đánh dấu `Completed` khi tất cả task con bắt buộc đã hoàn thành.
- Báo cáo task con phải khai báo `Parent task`; task gốc ghi `Không có`.
- Task bị hủy vẫn giữ nguyên ID và sử dụng trạng thái `Cancelled`.

Ví dụ:

```text
TASK-001 — Project Foundation
├── TASK-001-01 — Codebase Bootstrap
└── TASK-001-02 — Task Report Structure
    └── TASK-001-02-01 — Create Report Template
```

## Quy ước tên file và lưu trữ

- Dùng ngày thực hiện task theo định dạng `YYYY/MM/DD`.
- Đặt tên file theo mẫu `TASK-NNN[-NN[-NN]]-short-description.md`.
- Tên file dùng chữ thường, không dấu và phân tách bằng dấu gạch ngang.
- Phần mô tả phải ngắn gọn, thể hiện mục tiêu chính và không vượt quá 50 ký tự.
- Một báo cáo mô tả một task có phạm vi rõ ràng.
- Báo cáo phải được commit cùng với thay đổi thuộc task.
- Không bắt buộc ghi commit hash trong báo cáo vì hash chỉ được tạo sau khi commit hoàn thành.
- Không sửa lại báo cáo cũ để phản ánh task mới; hãy tạo báo cáo mới.

## Tạo báo cáo mới

1. Tạo thư mục ngày nếu chưa tồn tại.
2. Sao chép nội dung từ `templates/task-report-template.md`.
3. Xác định task cha và lấy số thứ tự chưa được sử dụng trong đúng phạm vi.
4. Đặt tên file theo mẫu `TASK-NNN[-NN[-NN]]-short-description.md`.
5. Hoàn thiện các mục bắt buộc trước khi commit.
