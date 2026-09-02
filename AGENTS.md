# AGENTS.md

## Human-Controlled Implementation Policy

### Nguyên tắc mặc định

Agent hoạt động ở chế độ tư vấn. Agent không được tự tạo, sửa, xóa hoặc chèn code nghiệp vụ hay code kỹ thuật có khả năng thay đổi hành vi của hệ thống.

Mọi production code phải được chủ dự án xem xét, sao chép thủ công và chạy thử.

### Agent được phép

Agent chỉ được trực tiếp thay đổi các nhóm file sau:

- Tài liệu Markdown.
- README và tài liệu kiến trúc.
- ADR, standards và task reports.
- File placeholder trống.
- Cấu trúc thư mục.
- Template không chứa production logic.
- Test script hoặc test fixture khi được người dùng yêu cầu rõ ràng.
- Comment và đề xuất sửa đổi không làm thay đổi runtime behavior.

### Agent không được phép

Nếu không có chỉ thị ngoại lệ rõ ràng, agent không được:

- Sửa code nghiệp vụ.
- Sửa code data pipeline, transformation hoặc orchestration.
- Sửa Infrastructure as Code.
- Sửa schema, migration hoặc data contract đang được sử dụng.
- Sửa cấu hình runtime, deployment hoặc CI/CD.
- Thay đổi dependency hoặc version package.
- Chạy migration, deployment, backfill hoặc pipeline ghi dữ liệu.
- Tự động áp dụng snippet đã đề xuất.
- Chạy script có khả năng ghi, xóa hoặc thay đổi dữ liệu thật.
- Dùng formatter, generator hoặc autofix nếu công cụ đó có thể sửa production code.
- Xóa, đổi tên hoặc di chuyển production file.

### Cách xử lý yêu cầu thay đổi code

Khi xác định cần thay đổi production code, agent phải:

1. Đọc và phân tích code hiện tại.
2. Giải thích vấn đề và nguyên nhân.
3. Đề xuất giải pháp.
4. Cung cấp snippet hoặc diff minh họa.
5. Nêu chính xác file và vị trí cần chèn hoặc thay thế.
6. Nêu tác động, rủi ro và phương án rollback.
7. Đề xuất cách kiểm thử.
8. Dừng lại để chủ dự án tự áp dụng thay đổi.

Agent không được tự áp dụng snippet hoặc diff đó vào repository.

### Quyền đọc và kiểm tra

Agent được phép:

- Đọc source code, cấu hình, log và test result.
- Tìm kiếm dependency và vị trí sử dụng code.
- Chạy các lệnh kiểm tra chỉ đọc.
- Chạy test không làm thay đổi dữ liệu hoặc external state.
- Review code đã được chủ dự án tự thêm vào.
- Phân tích lỗi và đề xuất cách sửa.

### Test code

Agent chỉ được tạo hoặc sửa test khi người dùng yêu cầu rõ ràng.

Test do agent tạo phải:

- Không truy cập production environment.
- Không sử dụng credential thật.
- Không sửa hoặc xóa dữ liệu thật.
- Dùng mock, stub, sandbox hoặc synthetic fixture khi phù hợp.
- Ghi rõ lệnh chạy và kết quả mong đợi.
- Không tự động thay đổi production code để làm test pass.

### Ngoại lệ

Ngoại lệ chỉ có hiệu lực khi người dùng cho phép rõ ràng trong task hiện tại và chỉ áp dụng cho đúng file hoặc phạm vi được nêu.

Một yêu cầu chung như “hãy sửa lỗi này” không mặc nhiên cho phép agent chỉnh production code. Người dùng phải nói rõ rằng agent được phép trực tiếp sửa code.

Khi phạm vi cho phép không rõ ràng, agent phải giữ chế độ tư vấn.

## Phân loại quyền theo khu vực

| Nhóm | Quyền mặc định |
|---|---|
| `docs/**`, `*.md` | Được sửa |
| `docs/task-reports/**` | Được tạo và sửa |
| Placeholder trống | Được tạo |
| `tests/**` | Chỉ sửa khi được yêu cầu rõ ràng |
| `src/**` | Chỉ đọc, không sửa |
| `ingestion/**` | Chỉ đọc, không sửa |
| `transformation/**` | Chỉ đọc, không sửa |
| `orchestration/**` | Chỉ đọc, không sửa |
| `analytics/**` | Chỉ đọc, không sửa logic |
| `infrastructure/**` | Chỉ đọc, không sửa |
| Runtime configuration và CI/CD | Chỉ đọc, không sửa |
| Dữ liệu thật | Không được ghi hoặc xóa |

## Chuẩn trình bày đề xuất thay đổi

Khi đề xuất thay đổi production code, agent nên trình bày theo cấu trúc sau:

```markdown
## Đề xuất thay đổi

- File: `path/to/file`
- Vị trí: mô tả vị trí cần thay đổi
- Mục đích: mô tả mục tiêu
- Trạng thái: CHƯA ĐƯỢC ÁP DỤNG

### Snippet đề xuất

Snippet để chủ dự án tự xem xét và sao chép.

### Tác động và rủi ro

- Mô tả tác động và rủi ro liên quan.

### Phương án rollback

- Mô tả cách hoàn tác an toàn.

### Cách kiểm thử

1. Các bước kiểm thử.
2. Kết quả mong đợi.
```

## Quy tắc đối với placeholder

Placeholder không được chứa production logic hoặc code mẫu có thể bị hiểu nhầm là code sẵn sàng sử dụng.

Nếu cần nội dung để giải thích mục đích, chỉ sử dụng comment rõ ràng như:

```text
Placeholder only — production implementation must be added manually.
```

