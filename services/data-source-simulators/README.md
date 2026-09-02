# Data Source Simulators

Khu vực này chứa các service và script dùng để mô phỏng (simulate) hoặc sinh (generate) dữ liệu nguồn cho FMCG Data Platform.

## Trách nhiệm

- Đóng vai các hệ thống nghiệp vụ (ERP, POS, DMS, Web Services, v.v.).
- Sinh dữ liệu synthetic (giả lập) hoặc cung cấp dữ liệu mẫu theo miền (sales, inventory, product, v.v.).
- Cung cấp dữ liệu ra ngoài thông qua các giao diện chuẩn (API, Event Stream, File Batch, CDC/Database) đã được định nghĩa trong `contracts/`.

## Tổ chức Codebase

Codebase được tổ chức theo mô hình **source-system-first**:

- `simple-generators/`: Chứa các bộ sinh dữ liệu đơn giản ban đầu, đóng vai trò như hệ thống nguồn tối thiểu (MVP).
- `shared/`: Chứa các khái niệm, tiện ích, data model dùng chung giữa các simulator. (Chỉ thêm vào đây khi có ít nhất 2 consumer).
- `[tên-hệ-thống-nguồn]/` (ví dụ `odoo-erp`, `mock-web-service`): Các hệ thống mô phỏng phức tạp hoặc tích hợp đầy đủ sẽ được đặt thành thư mục ngang hàng với `simple-generators`.

## Nguyên tắc thiết kế

- Không phụ thuộc vào luồng dữ liệu Ingestion của nền tảng (simulator không biết ai đang lấy dữ liệu của mình).
- Giao tiếp qua data contract có phiên bản.
- Có thể chạy độc lập từng hệ thống nguồn.
- Không chứa dữ liệu production hay credentials thật.
