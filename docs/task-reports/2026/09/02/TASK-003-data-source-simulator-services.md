# TASK-003 — Tạo cấu trúc Data Source Simulator Services

## Thông tin

- Ngày tạo: 2026-09-02
- Ngày thực hiện: Chưa thực hiện
- Trạng thái: Planned
- Người thực hiện: Chưa phân công
- Parent task: Không có
- Task/Issue: TASK-003

## Mục tiêu

Tạo khu vực chứa các service giả lập nguồn dữ liệu FMCG để phục vụ phát triển và kiểm thử cục bộ trong các giai đoạn tiếp theo.

Task này chỉ xây dựng cấu trúc thư mục, placeholder và tài liệu mô tả trách nhiệm. Không triển khai logic sinh dữ liệu, API, dependency, cấu hình runtime, container hoặc CI/CD.

## Phạm vi thực hiện

- Tạo thư mục gốc `services/data-source-simulators/`.
- Tạo các khu vực service ban đầu:
  - `sales-pos/`: giả lập giao dịch bán hàng hoặc POS.
  - `product-master/`: giả lập dữ liệu danh mục sản phẩm và SKU.
  - `outlet-customer/`: giả lập dữ liệu khách hàng, nhà phân phối và điểm bán.
  - `inventory/`: giả lập tồn kho và biến động tồn kho.
  - `promotion/`: giả lập chương trình khuyến mãi.
- Thêm README cho thư mục gốc và từng service để mô tả trách nhiệm, ranh giới và đầu ra dự kiến.
- Cập nhật README cấp repository để phản ánh cấu trúc mới.
- Chỉ sử dụng placeholder hợp lệ theo `AGENTS.md` nếu cần giữ thư mục rỗng.

## Ngoài phạm vi

- Viết production logic hoặc code sinh dữ liệu.
- Lựa chọn ngôn ngữ, framework hoặc thư viện.
- Định nghĩa schema hoặc data contract sẵn sàng sử dụng.
- Tạo API endpoint, message broker integration hoặc database integration.
- Tạo Dockerfile, Infrastructure as Code, runtime configuration hoặc CI/CD.
- Tạo hay chỉnh sửa test.
- Sinh hoặc ghi dữ liệu thật.

## Cấu trúc đề xuất

```text
services/
└── data-source-simulators/
    ├── README.md
    ├── sales-pos/
    │   └── README.md
    ├── product-master/
    │   └── README.md
    ├── outlet-customer/
    │   └── README.md
    ├── inventory/
    │   └── README.md
    └── promotion/
        └── README.md
```

Cấu trúc này là đề xuất cho task và có thể được chủ dự án điều chỉnh trước khi triển khai.

## Files dự kiến thay đổi

- `README.md`
- `services/data-source-simulators/README.md`
- `services/data-source-simulators/sales-pos/README.md`
- `services/data-source-simulators/product-master/README.md`
- `services/data-source-simulators/outlet-customer/README.md`
- `services/data-source-simulators/inventory/README.md`
- `services/data-source-simulators/promotion/README.md`
- `docs/task-reports/2026/09/02/TASK-003-data-source-simulator-services.md`

## Quyết định kỹ thuật

- Giữ cấu trúc trung lập về công nghệ cho đến khi kiến trúc và technology stack được phê duyệt.
- Tách simulator theo domain nguồn dữ liệu để mỗi service có thể phát triển và vận hành độc lập trong tương lai.
- Không đặt simulator trong `ingestion/` vì simulator đại diện cho hệ thống nguồn, còn ingestion chịu trách nhiệm đưa dữ liệu từ nguồn vào data platform.

## Tiêu chí hoàn thành

- [ ] Có thư mục gốc dành riêng cho data source simulators.
- [ ] Có đủ năm khu vực service ban đầu theo phạm vi task.
- [ ] Mỗi thư mục có README mô tả rõ trách nhiệm và không chứa production logic.
- [ ] README cấp repository phản ánh đúng cấu trúc mới.
- [ ] Không có dependency, runtime configuration, test hoặc executable code mới.
- [ ] Tất cả placeholder tuân thủ `AGENTS.md`.
- [ ] Kiểm tra thủ công xác nhận cấu trúc và đường dẫn đúng.

## Kiểm thử dự kiến

- [ ] Static checks hoặc lint — Không áp dụng nếu task chỉ thay đổi Markdown và thư mục.
- [ ] Unit tests — Không áp dụng vì không có executable code.
- [ ] Integration tests — Không áp dụng vì không có tích hợp runtime.
- [ ] Kiểm tra thủ công — Xác nhận cấu trúc thư mục, nội dung README và phạm vi thay đổi.

## Kết quả

Chưa thực hiện. Kết quả sẽ được cập nhật khi task được triển khai.

## Rủi ro và phương án rollback

- Rủi ro: cấu trúc domain có thể thay đổi sau khi business requirements và data contracts được xác định.
- Rollback: xóa các thư mục placeholder mới và hoàn tác phần mô tả tương ứng trong README; không có tác động runtime hoặc dữ liệu.

## Hạn chế và công việc tiếp theo

- Xác định source systems và dữ liệu tối thiểu cần giả lập cho từng domain.
- Thiết kế data contract sau khi business context được thống nhất.
- Lựa chọn technology stack trước khi triển khai simulator logic.
