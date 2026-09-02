# TASK-004 — Thiết kế codebase Data Source Simulators

## Thông tin

- Ngày tạo: 2026-09-02
- Ngày thực hiện: 2026-09-02
- Trạng thái: Completed
- Người thực hiện: Antigravity
- Parent task: Không có
- Task/Issue: TASK-004

## Bối cảnh

Data platform cần các nguồn dữ liệu giả lập để phát triển và kiểm thử luồng dữ liệu end-to-end mà không phụ thuộc vào hệ thống production. Giai đoạn đầu cần hỗ trợ generator đơn giản theo domain FMCG; về sau phải có khả năng bổ sung các source system hoàn chỉnh như Odoo ERP, POS, Distributor Management System hoặc mock web service.

Codebase cần phân biệt rõ:

- **Source simulator:** đóng vai hệ thống bên ngoài và sinh hoặc cung cấp dữ liệu.
- **Ingestion connector:** tiếp nhận dữ liệu từ source system vào data platform.
- **Data contract:** mô tả giao diện trao đổi giữa source và ingestion.

## Mục tiêu

Nghiên cứu, xác nhận và tạo cấu trúc codebase trung lập về công nghệ cho `data-source-simulators` theo hướng source-system-first. Cấu trúc phải hỗ trợ generator đơn giản ở giai đoạn đầu và cho phép mỗi ERP hoặc web service hoàn chỉnh được phát triển thành một service độc lập trong tương lai.

Task này chỉ cho phép tạo cấu trúc thư mục, placeholder hợp lệ và tài liệu Markdown. Không triển khai executable code hoặc thay đổi hành vi runtime.

## Phạm vi nghiên cứu

- Xác định ranh giới giữa simulator, ingestion và transformation.
- Đánh giá cách tổ chức theo domain so với tổ chức theo source system.
- Xác định các thành phần dùng chung tối thiểu giữa simulator.
- Xác định vị trí dự kiến cho data contract của API, event, file và database/CDC.
- Xác định convention để bổ sung một source system mới mà không ảnh hưởng source system hiện có.
- Xác định các interface dữ liệu dự kiến: batch file, API, event stream và database/CDC.
- Ghi nhận những quyết định phụ thuộc vào kết quả lựa chọn technology stack.

## Phạm vi triển khai cấu trúc

- Tạo `services/data-source-simulators/` làm khu vực gốc cho các source simulator.
- Tạo `simple-generators/` cho các generator synthetic ban đầu.
- Tạo `shared/` cho các khái niệm dùng chung; chưa chứa implementation.
- Tạo README mô tả trách nhiệm và ranh giới của từng khu vực.
- Thêm placeholder cho những source system được xác nhận triển khai ngay; không tạo hàng loạt service chưa có kế hoạch.
- Tạo khu vực `contracts/` ở cấp repository nếu được phê duyệt sau nghiên cứu.
- Cập nhật README cấp repository để phản ánh cấu trúc thực tế.

## Kiến trúc codebase đề xuất

```text
services/
└── data-source-simulators/
    ├── README.md
    ├── shared/
    │   └── README.md
    └── simple-generators/
        ├── README.md
        ├── sales-pos/
        │   └── README.md
        ├── inventory/
        │   └── README.md
        ├── product-master/
        │   └── README.md
        ├── outlet-customer/
        │   └── README.md
        └── promotion/
            └── README.md

contracts/
├── README.md
├── events/
├── api/
├── files/
└── database/
```

Khi có task triển khai riêng, một source system hoàn chỉnh được bổ sung ngang hàng với `simple-generators/`:

```text
services/data-source-simulators/
├── simple-generators/
├── odoo-erp/
│   ├── README.md
│   ├── app/
│   ├── seed/
│   ├── scenarios/
│   ├── exports/
│   └── deployment/
└── mock-web-service/
    ├── README.md
    ├── app/
    ├── seed/
    ├── scenarios/
    └── deployment/
```

Các thư mục `app/`, `seed/`, `scenarios/`, `exports/` và `deployment/` chỉ được tạo khi source system thực sự cần chúng. Task này không tạo Odoo hoặc mock web service implementation.

## Nguyên tắc thiết kế cần xác nhận

- Tổ chức cấp cao theo source system, không trộn nhiều hệ thống nguồn trong cùng một service.
- Business domain nằm bên trong source system khi source đó cung cấp nhiều domain.
- Simulator không phụ thuộc trực tiếp vào implementation của ingestion pipeline.
- Giao tiếp giữa simulator và ingestion tuân theo data contract có version.
- Mỗi source system có thể chạy, cấu hình, seed và dừng độc lập.
- Dữ liệu mặc định phải synthetic, không chứa credential hoặc dữ liệu production.
- Batch và streaming là các delivery mode, không phải lý do để nhân đôi source system.
- Thành phần trong `shared/` chỉ được bổ sung khi có ít nhất hai consumer thực tế.

## Ngoài phạm vi

- Viết logic sinh dữ liệu hoặc code service.
- Cài đặt hay cấu hình Odoo, database, API server hoặc message broker.
- Lựa chọn hoặc thay đổi dependency và version package.
- Tạo Dockerfile, Docker Compose, Infrastructure as Code hoặc CI/CD.
- Định nghĩa data contract sẵn sàng sử dụng trong production.
- Tạo ingestion connector, transformation hoặc orchestration workflow.
- Tạo hay chỉnh sửa test.
- Kết nối production environment hoặc ghi dữ liệu thật.

## Dependency và quan hệ với task khác

- Kết quả nghiên cứu technology stack trong `TASK-003-technology-stack-selection.md` là đầu vào trước khi triển khai executable code.
- Task này thay thế phạm vi kiến trúc domain-first được đề xuất trong `TASK-003-data-source-simulator-services.md` bằng hướng source-system-first.
- Xung đột ID giữa hai file `TASK-003` hiện có phải được xử lý riêng theo quy ước quản lý task; task này không tự sửa hoặc đổi tên lịch sử đó.

## Deliverables

- Tài liệu kết luận về ranh giới và cách tổ chức source simulator.
- Cấu trúc thư mục được phê duyệt cho `services/data-source-simulators/`.
- README cấp simulator và cấp khu vực con.
- Khu vực `contracts/` nếu quyết định được phê duyệt.
- README cấp repository được cập nhật.
- Danh sách follow-up task cho simple generator, Odoo ERP, mock web service, data contract và continuous data generation.

## Files dự kiến thay đổi

- `README.md`
- `services/data-source-simulators/README.md`
- `services/data-source-simulators/shared/README.md`
- `services/data-source-simulators/simple-generators/README.md`
- `services/data-source-simulators/simple-generators/*/README.md`
- `contracts/README.md` nếu được phê duyệt
- `docs/task-reports/2026/09/02/TASK-004-data-source-simulators-codebase.md`

## Quyết định kỹ thuật

- Đề xuất tổ chức source-system-first để Odoo, POS, web service và các hệ thống tương lai có ranh giới triển khai rõ ràng.
- Duy trì `simple-generators/` như một source simulator phục vụ MVP, thay vì đặt từng domain ngang hàng với các ERP hoàn chỉnh.
- Đặt data contract ngoài simulator và ingestion để hai phía không sở hữu độc quyền giao diện trao đổi.
- Quyết định cuối cùng chỉ có hiệu lực sau khi chủ dự án review; nếu là quyết định kiến trúc dài hạn, cần được ghi nhận bằng ADR riêng.

## Tiêu chí nghiệm thu

- [x] Ranh giới giữa simulator, ingestion và transformation được mô tả rõ.
- [x] Codebase sử dụng cấu trúc source-system-first đã được chủ dự án phê duyệt.
- [x] Có khu vực riêng cho simple generators và shared concepts.
- [x] Có convention rõ ràng để bổ sung Odoo hoặc một web service mới.
- [x] Không có source system chưa được phê duyệt bị tạo dư thừa.
- [x] README của từng khu vực mô tả trách nhiệm và nội dung ngoài phạm vi.
- [x] README cấp repository phản ánh đúng cấu trúc thực tế.
- [x] Không có executable code, dependency hoặc runtime configuration được thêm.
- [x] Không có production data hoặc credential được tạo hay ghi lại.
- [x] Placeholder tuân thủ `AGENTS.md`.
- [x] Các follow-up task và dependency được ghi nhận.

## Kiểm thử dự kiến

- [ ] Static checks hoặc lint — Không áp dụng nếu chỉ có Markdown và cấu trúc thư mục.
- [ ] Unit tests — Không áp dụng vì không có executable code.
- [ ] Integration tests — Không áp dụng vì chưa có source integration.
- [x] Kiểm tra thủ công — Đã đối chiếu cây thư mục, README, phạm vi và chính sách trong `AGENTS.md`.

## Kết quả

Đã thiết lập cấu trúc cho `services/data-source-simulators/` và `contracts/` theo thiết kế source-system-first. Phạm vi thay đổi chỉ gồm cấu trúc thư mục, placeholder và tài liệu Markdown; không có executable code hoặc thay đổi runtime.

## Rủi ro và phương án rollback

- Rủi ro: tạo abstraction trong `shared/` quá sớm có thể làm các simulator bị phụ thuộc không cần thiết.
- Rủi ro: data contract được thiết kế trước khi chọn delivery mode có thể phải thay đổi.
- Rủi ro: cấu trúc Odoo giả định trước cách triển khai thực tế có thể gây dư thừa thư mục.
- Rollback: xóa các placeholder mới và hoàn tác phần tài liệu tương ứng; task này không tạo runtime impact hoặc thay đổi dữ liệu.

## Hạn chế và công việc tiếp theo

- Hoàn thành và phê duyệt technology stack trước khi viết implementation.
- Tạo task riêng cho data contract và versioning policy.
- Tạo task riêng cho simple synthetic generators.
- Tạo task riêng cho continuous data generation và failure scenarios.
- Tạo task riêng cho từng source system hoàn chỉnh, ví dụ Odoo ERP hoặc mock web service.
