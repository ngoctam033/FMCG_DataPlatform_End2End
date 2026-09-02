# FMCG Data Platform End-to-End

> Xây dựng nền tảng dữ liệu end-to-end cho ngành hàng tiêu dùng nhanh (FMCG), từ nền móng kỹ thuật đến các sản phẩm dữ liệu hỗ trợ doanh nghiệp ra quyết định.

## Tổng quan

FMCG Data Platform End-to-End là dự án xây dựng một nền tảng dữ liệu có khả năng thu thập, lưu trữ, xử lý và cung cấp dữ liệu đáng tin cậy cho hoạt động phân tích trong doanh nghiệp FMCG.

Dự án được phát triển theo hai hướng nối tiếp và bổ trợ lẫn nhau:

1. **Xây dựng nền tảng kỹ thuật:** thiết lập kiến trúc và các thành phần cốt lõi của một data platform hiện đại.
2. **Phát triển business case:** sử dụng nền tảng để giải quyết các bài toán thực tế và tạo ra giá trị cho doanh nghiệp.

## Mục tiêu

- Xây dựng luồng dữ liệu hoàn chỉnh từ nguồn đến lớp phục vụ người dùng.
- Chuẩn hóa dữ liệu bán hàng, sản phẩm, khách hàng, phân phối, tồn kho và khuyến mãi.
- Đảm bảo dữ liệu có chất lượng, có thể theo dõi và dễ dàng mở rộng.
- Tạo nguồn dữ liệu thống nhất phục vụ báo cáo, BI, phân tích nâng cao và machine learning.
- Chuyển dữ liệu thành insight và hành động có giá trị cho doanh nghiệp FMCG.
- Xây dựng một dự án thực tế có thể dùng để học tập, thử nghiệm và trình diễn năng lực Data Engineering/Data Platform.

## Lộ trình phát triển

### Giai đoạn 1 — Technical Foundation

Giai đoạn đầu tập trung xây dựng nền móng kỹ thuật:

- Mô phỏng hoặc tích hợp các nguồn dữ liệu đặc trưng của FMCG.
- Xây dựng pipeline ingestion theo batch và, khi phù hợp, streaming.
- Thiết kế các lớp lưu trữ và mô hình dữ liệu.
- Làm sạch, chuẩn hóa và chuyển đổi dữ liệu.
- Điều phối workflow và quản lý dependency giữa các pipeline.
- Kiểm thử và giám sát chất lượng dữ liệu.
- Quản lý metadata, lineage, logging và cảnh báo.
- Tự động hóa kiểm thử và triển khai bằng CI/CD.
- Cung cấp lớp dữ liệu phục vụ BI, analytics và các ứng dụng phía sau.

### Giai đoạn 2 — Business Use Cases

Khi nền tảng kỹ thuật đủ ổn định, dự án sẽ mở rộng sang các bài toán kinh doanh, dự kiến gồm:

- Phân tích doanh thu và lợi nhuận theo sản phẩm, SKU, kênh và khu vực.
- Theo dõi hiệu suất nhà phân phối và độ phủ điểm bán.
- Phân tích tồn kho, thiếu hàng và hàng chậm luân chuyển.
- Dự báo nhu cầu và hỗ trợ lập kế hoạch cung ứng.
- Đánh giá hiệu quả chương trình khuyến mãi.
- Phân khúc khách hàng hoặc điểm bán.
- Phát hiện bất thường và xây dựng hệ thống cảnh báo.
- Xây dựng dashboard và data product hỗ trợ ra quyết định.

Danh sách trên là định hướng ban đầu và sẽ được ưu tiên dựa trên giá trị kinh doanh, dữ liệu sẵn có và độ phức tạp khi triển khai.

## Kiến trúc mục tiêu

```text
Data Sources
    │
    ▼
Data Ingestion
    │
    ▼
Raw Storage
    │
    ▼
Data Processing & Quality
    │
    ▼
Curated Data / Data Warehouse
    │
    ├──► BI & Reporting
    ├──► Business Analytics
    ├──► Machine Learning
    └──► Data Products / APIs

Cross-cutting: Orchestration · Metadata · Lineage · Security · Monitoring · CI/CD
```

Kiến trúc và công nghệ cụ thể sẽ được ghi nhận thông qua các Architecture Decision Record (ADR) khi dự án phát triển.

## Miền dữ liệu dự kiến

| Miền dữ liệu | Ví dụ |
|---|---|
| Sản phẩm | Brand, category, SKU, packaging |
| Bán hàng | Order, invoice, quantity, revenue, discount |
| Khách hàng và điểm bán | Distributor, retailer, outlet, channel |
| Tồn kho | Stock level, movement, warehouse, stock-out |
| Khuyến mãi | Campaign, promotion mechanics, cost, uplift |
| Phân phối | Territory, route, delivery, sales representative |
| Dữ liệu tham chiếu | Calendar, geography, currency, unit of measure |

## Nguyên tắc thiết kế

- **Business-driven:** nền tảng kỹ thuật được thiết kế dựa trên nhu cầu kinh doanh có thể kiểm chứng.
- **Data quality by design:** chất lượng dữ liệu được kiểm soát trong từng lớp của pipeline.
- **Reproducible:** môi trường, pipeline và kết quả xử lý có thể tái tạo.
- **Observable:** hệ thống có logging, metrics, cảnh báo và khả năng truy vết lỗi.
- **Modular:** các thành phần có thể phát triển, kiểm thử và thay thế độc lập.
- **Scalable:** thiết kế cho phép mở rộng về dữ liệu, workload và số lượng use case.
- **Secure by default:** quyền truy cập và dữ liệu nhạy cảm được quản lý ngay từ đầu.

## Cấu trúc repository

Codebase ban đầu được tổ chức theo trách nhiệm và giữ trung lập về công nghệ:

```text
├── analytics/         # Semantic models, BI assets và data products
├── config/            # Cấu hình dùng chung, không chứa thông tin bí mật
├── contracts/         # Data contracts định nghĩa giao tiếp dữ liệu
├── data/              # Dữ liệu phát triển cục bộ, không commit lên Git
├── docs/              # Kiến trúc, ADR, standards, business và task reports
├── infrastructure/    # Infrastructure as Code và cấu hình triển khai
├── ingestion/         # Connector và pipeline thu thập dữ liệu
├── orchestration/     # Workflow, lịch chạy và dependency
├── quality/           # Data quality rules và validation suites
├── scripts/           # Tiện ích phát triển và vận hành
├── services/          # Các backend services (ví dụ: data-source-simulators)
├── src/               # Mã nguồn dùng chung của platform
├── tests/             # Integration, contract và end-to-end tests
├── transformation/    # Làm sạch, chuẩn hóa và mô hình hóa dữ liệu
├── .env.example       # Mẫu biến môi trường cục bộ
├── .gitignore
└── README.md          # Điểm bắt đầu của dự án
```

Mỗi khu vực có README riêng mô tả trách nhiệm. Package và cấu hình đặc thù công nghệ sẽ được bổ sung sau khi có quyết định kiến trúc đầu tiên.

## Bắt đầu

Dự án đang ở giai đoạn khởi tạo. Hướng dẫn cài đặt và chạy cục bộ sẽ được cập nhật sau khi kiến trúc và technology stack đầu tiên được lựa chọn.

Các bước tiếp theo:

1. Xác định business context và phạm vi dữ liệu mẫu.
2. Xác định yêu cầu chức năng và phi chức năng.
3. Lựa chọn kiến trúc cùng technology stack cho MVP.
4. Thiết kế mô hình dữ liệu cấp cao.
5. Xây dựng vertical slice đầu tiên từ nguồn dữ liệu đến báo cáo.
6. Bổ sung kiểm thử, monitoring, tài liệu và CI/CD.

## Trạng thái dự án

🚧 **Khởi tạo — đang xác định kiến trúc, phạm vi MVP và technology stack.**

## Đóng góp

Quy ước phát triển, branching strategy, coding standards và quy trình đóng góp sẽ được bổ sung khi repository có những thành phần triển khai đầu tiên.

## License

Chưa xác định. Thông tin giấy phép sẽ được cập nhật trước khi dự án được phân phối hoặc mở cho đóng góp rộng rãi.
