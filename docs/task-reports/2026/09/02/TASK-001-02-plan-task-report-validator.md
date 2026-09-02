# TASK-001-02 — Lập kế hoạch script kiểm tra Task Report

## Thông tin

- Ngày thực hiện: 2026-09-02
- Trạng thái: Planned
- Người thực hiện: Codex
- Parent task: TASK-001
- Task/Issue: Lập kế hoạch xây dựng script kiểm tra cú pháp file Markdown báo cáo task

## Mục tiêu

Xác định phạm vi, quy tắc kiểm tra, giao diện thực thi và tiêu chí nghiệm thu cho một script kiểm tra tự động cú pháp và cấu trúc của các file Markdown trong `docs/task-reports/`.

Task này chỉ tạo kế hoạch. Script kiểm tra và test liên quan chưa được triển khai.

## Phạm vi dự kiến

Script sẽ kiểm tra các báo cáo task tại:

```text
docs/task-reports/YYYY/MM/DD/TASK-NNN[-NN[-NN]]-short-description.md
```

Không kiểm tra:

- `docs/task-reports/README.md`.
- Nội dung template tại `docs/task-reports/templates/` như một task report thực tế.
- Các file Markdown nằm ngoài `docs/task-reports/`.
- Tính đúng đắn về mặt nghiệp vụ của nội dung báo cáo.

## Quy tắc cần kiểm tra

### 1. Đường dẫn

- Báo cáo nằm đúng cây thư mục `YYYY/MM/DD`.
- Các thành phần năm, tháng và ngày tạo thành một ngày hợp lệ.
- Trường `Ngày thực hiện` trong báo cáo trùng với ngày trên đường dẫn.

### 2. Tên file và Task ID

- Tên file tuân theo mẫu `TASK-NNN[-NN[-NN]]-short-description.md`.
- Task gốc dùng ba chữ số; mỗi cấp task con dùng hai chữ số.
- Không vượt quá hai cấp task con.
- Phần mô tả chỉ gồm chữ thường ASCII, chữ số và dấu gạch ngang.
- Phần mô tả không dài quá 50 ký tự.
- Task ID trong tiêu đề trùng với Task ID trong tên file.
- Không tồn tại Task ID trùng lặp trong toàn bộ thư mục báo cáo.

### 3. Quan hệ task cha–con

- Task gốc khai báo `Parent task: Không có`.
- Task con khai báo đúng Task ID của task cha trực tiếp.
- Báo cáo của task cha phải tồn tại.
- Task cha không được trỏ đến chính task con hoặc tạo quan hệ vòng.

### 4. Cấu trúc Markdown

Báo cáo phải có đúng một tiêu đề cấp 1 theo mẫu:

```markdown
# TASK-NNN[-NN[-NN]] — Task title
```

Các section bắt buộc:

```text
## Thông tin
## Mục tiêu
## Thay đổi đã thực hiện
## Files changed
## Quyết định kỹ thuật
## Kiểm thử
## Kết quả
## Hạn chế và công việc tiếp theo
```

### 5. Metadata bắt buộc

Section `Thông tin` phải có:

- `Ngày thực hiện` theo định dạng `YYYY-MM-DD`.
- `Trạng thái` thuộc danh sách trạng thái được hỗ trợ.
- `Người thực hiện` không được để trống.
- `Parent task` theo đúng quan hệ phân cấp.
- `Task/Issue` không được để trống.

Danh sách trạng thái dự kiến:

```text
Planned
In Progress
Completed
Cancelled
Blocked
```

### 6. Nội dung tối thiểu

- Các section bắt buộc không được để trống.
- `Files changed` phải sử dụng danh sách Markdown và đường dẫn đặt trong backtick.
- `Kiểm thử` phải chứa ít nhất một checklist item.
- Task ở trạng thái `Completed` phải có mô tả tại section `Kết quả`.

## Hành vi CLI dự kiến

Giao diện cuối cùng sẽ được quyết định khi lựa chọn ngôn ngữ triển khai. Hành vi mong muốn:

```text
<validator-command> [file-or-directory]
```

- Không có tham số: kiểm tra toàn bộ `docs/task-reports/`.
- Nhận một file: chỉ kiểm tra báo cáo được chỉ định.
- Nhận một thư mục: kiểm tra đệ quy các báo cáo trong thư mục.
- Exit code `0`: tất cả báo cáo hợp lệ.
- Exit code khác `0`: có ít nhất một lỗi hoặc script không thể hoàn tất kiểm tra.
- Mỗi lỗi hiển thị đường dẫn file, quy tắc vi phạm và thông báo có thể hành động.
- Sắp xếp lỗi ổn định theo đường dẫn và vị trí để kết quả dễ tái tạo.

## Phân loại kết quả

- **Error:** vi phạm cấu trúc bắt buộc, làm exit code thất bại.
- **Warning:** nội dung chưa tối ưu nhưng không vi phạm cú pháp bắt buộc.
- **Passed:** không phát hiện vi phạm.

Danh sách warning cụ thể sẽ được xác định trong task triển khai; phiên bản đầu tiên nên ưu tiên các error có tính xác định cao.

## Kế hoạch triển khai

1. Chốt ngôn ngữ và vị trí của script sau khi technology stack được xác định.
2. Chuyển các quy tắc trong tài liệu thành rule ID ổn định.
3. Xây dựng bộ parser cho đường dẫn, tên file, heading, metadata và section.
4. Xây dựng kiểm tra toàn repository cho ID trùng và quan hệ cha–con.
5. Thêm thông báo lỗi và exit code phù hợp cho local development.
6. Tạo synthetic fixtures hợp lệ và không hợp lệ.
7. Tạo test cho từng rule và các trường hợp biên.
8. Chạy thử cục bộ trên toàn bộ task report hiện có.
9. Viết hướng dẫn sử dụng và cách xử lý lỗi.
10. Chỉ tích hợp CI/CD trong một task riêng sau khi được chủ dự án phê duyệt rõ ràng.

## Test cases dự kiến

- Báo cáo task gốc hợp lệ.
- Báo cáo task con cấp 1 và cấp 2 hợp lệ.
- Sai định dạng thư mục ngày hoặc ngày không tồn tại.
- Ngày trong metadata không trùng đường dẫn.
- Sai tiền tố, số lượng chữ số hoặc độ sâu task.
- Slug có chữ hoa, khoảng trắng, ký tự có dấu hoặc quá dài.
- Task ID trong tiêu đề khác tên file.
- Task ID bị trùng.
- Task con thiếu parent, sai parent hoặc parent không tồn tại.
- Thiếu heading, section hoặc metadata bắt buộc.
- Metadata có giá trị rỗng hoặc trạng thái không được hỗ trợ.
- Task `Completed` không có kết quả.
- File template và README được loại trừ đúng cách.

## Tiêu chí nghiệm thu cho task triển khai

- Tất cả quy tắc bắt buộc đã chốt đều có rule ID và test tương ứng.
- Script kiểm tra được một file và toàn bộ thư mục báo cáo.
- Script trả exit code ổn định và phù hợp.
- Thông báo lỗi chỉ rõ file cùng nguyên nhân.
- Không đọc credential, không truy cập production environment và không thay đổi file được kiểm tra.
- Script chỉ đọc dữ liệu và không tự động sửa báo cáo.
- Có hướng dẫn chạy cục bộ cùng kết quả mong đợi.
- Toàn bộ task report hợp lệ trong repository vượt qua kiểm tra.

## Files changed

- `docs/task-reports/2026/09/02/TASK-001-02-plan-task-report-validator.md`

## Quyết định kỹ thuật

- Validator phải là công cụ chỉ đọc và không có chế độ autofix.
- Chưa lựa chọn ngôn ngữ hoặc framework cho đến khi technology stack của dự án được xác định.
- Việc tích hợp validator vào CI/CD nằm ngoài phạm vi task này và cần phê duyệt riêng.

## Kiểm thử

- [ ] Static checks hoặc lint — chưa áp dụng vì đây là tài liệu kế hoạch.
- [ ] Unit tests — sẽ thuộc task triển khai script.
- [ ] Integration tests — sẽ thuộc task tích hợp sau này.
- [x] Kiểm tra thủ công cấu trúc kế hoạch và sự phù hợp với quy ước Task Report.

## Kết quả

Đã có kế hoạch triển khai validator với phạm vi, quy tắc, hành vi CLI, test cases và tiêu chí nghiệm thu cụ thể. Chưa có script hoặc runtime behavior nào được thêm vào repository.

## Hạn chế và công việc tiếp theo

- Cần chủ dự án duyệt các quy tắc bắt buộc và danh sách trạng thái.
- Cần lựa chọn ngôn ngữ triển khai trước khi tạo script.
- Việc tạo test hoặc script phải được người dùng yêu cầu rõ ràng theo Human-Controlled Implementation Policy.

