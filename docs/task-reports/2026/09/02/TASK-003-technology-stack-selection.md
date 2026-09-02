# TASK-003 — Nghiên cứu và lựa chọn technology stack

## Thông tin

- Ngày tạo: 2026-09-02
- Trạng thái: Planned
- Người thực hiện: Chưa phân công
- Parent task: Không có
- Task/Issue: Đánh giá và đề xuất technology stack cho FMCG Data Platform End-to-End

## Bối cảnh

Dự án được phát triển theo hai giai đoạn:

1. Xây dựng nền tảng kỹ thuật dữ liệu end-to-end cho FMCG.
2. Phát triển các business case và data product hỗ trợ doanh nghiệp.

Codebase hiện được tổ chức theo trách nhiệm và chưa phụ thuộc vào một công nghệ cụ thể. Cần có báo cáo đánh giá trước khi tạo ADR hoặc triển khai production code.

## Ràng buộc đã được xác nhận

- Môi trường triển khai ban đầu là local.
- Ngân sách RAM cho toàn bộ hệ thống khoảng 36 GB; CPU sẽ được giới hạn vì tốc độ chưa phải ưu tiên.
- Các thành phần của hệ thống được đóng gói và chạy bằng Docker.
- Python là ngôn ngữ lập trình chủ đạo.
- Giai đoạn đầu chỉ có một nguồn dữ liệu là relational operational database; PostgreSQL là lựa chọn ưu tiên.
- Dữ liệu nguồn có nhiều bảng và relationship, nhằm mô phỏng hệ thống FMCG thực tế.
- Một service riêng sẽ sinh và ghi dữ liệu vào operational database theo nhiều chế độ: liên tục, theo phút, theo giờ và theo ngày.
- Kiến trúc ingestion phải hỗ trợ cả batch định kỳ và CDC; MVP triển khai batch trước.
- Độ trễ dữ liệu tối đa một ngày vẫn được chấp nhận; CDC được triển khai nhằm học tập và mô phỏng thực tế, không xuất phát từ SLA near-real-time bắt buộc.
- Kiến trúc dữ liệu đi theo hướng lakehouse.
- Phần lớn dữ liệu trong lakehouse được lưu ở định dạng Apache Parquet.
- Apache Iceberg là table format được triển khai đầu tiên.
- MinIO là object storage đầu tiên.
- MVP cần nghiên cứu time travel, schema evolution, partition evolution, update/delete/merge và concurrent writes.
- Hướng xử lý kết hợp SQL, Python/DataFrame và distributed processing; SQL là giao diện ưu tiên. MVP chỉ cần chuẩn bị kiến trúc cho distributed processing, chưa bắt buộc chạy processing cluster.
- Orchestration cần gần với cách vận hành trong doanh nghiệp.
- Data catalog và lineage nằm trong phạm vi giai đoạn đầu.
- Observability bao gồm logging, metrics, dashboard và alerting.
- Kiểm thử ưu tiên integration test, data quality test và data contract/business test.
- Đầu ra phân tích đầu tiên là dashboard Power BI. Power BI project được lưu trong repository/máy local và mở bằng Power BI Desktop miễn phí trên máy ảo Windows.
- Mọi thành phần phía data platform phải có khả năng chạy local, self-hosted và sử dụng bản open-source. Power BI Desktop miễn phí là ngoại lệ được chấp nhận cho lớp BI.
- Dữ liệu MVP ban đầu chỉ cần ở quy mô vài nghìn dòng; chưa đặt mục tiêu benchmark hiệu năng lớn.
- Security nâng cao chưa thuộc MVP và được đưa vào backlog của phase sau.
- Root Docker Compose cần chia profile tường minh để chỉ chạy các nhóm service cần thiết tại một thời điểm.
- Mục tiêu ưu tiên của giai đoạn đầu là xây dựng portfolio có thể trình diễn.
- Hệ thống phải cho phép thử nghiệm nhiều công nghệ cùng loại theo từng giai đoạn.
- Các implementation công nghệ cùng tồn tại trên một nhánh; một file cấu hình xác định implementation được sử dụng khi chạy.
- Repository sử dụng mô hình monorepo, tách thành nhiều service hoặc package.
- Mỗi service có Docker Compose riêng và root repository có Docker Compose tổng hợp để chạy toàn bộ hệ thống như một khối hoàn chỉnh.
- Không yêu cầu tất cả service chạy đồng thời. Người vận hành có thể dừng các service không cần thiết để quản lý tài nguyên trong giới hạn khoảng 36 GB RAM.

Ví dụ các nhóm công nghệ cần có khả năng thay thế:

- Table format: Apache Iceberg và Delta Lake.
- Object storage: dịch vụ tương thích S3 và MinIO.
- Các nhóm ingestion, processing, orchestration, catalog và query engine sẽ được xác định trong báo cáo.

Các nội dung trên là constraint đầu vào của task, không phải kết luận rằng mọi công nghệ được nêu đều phải chạy đồng thời trong cùng một nhánh.

## Technology baseline được lựa chọn cho giai đoạn hiện tại

Các công nghệ dưới đây tạo thành baseline stack cho MVP local-first. Đây là lựa chọn đầu vào cho thiết kế chi tiết và ADR; task này không cấp quyền triển khai hoặc thay đổi production code.

| Capability | Công nghệ | Vai trò trong giai đoạn hiện tại |
|---|---|---|
| Ngôn ngữ chính | Python | Service, ingestion, automation và integration code |
| Đóng gói và điều phối local | Docker, Docker Compose | Đóng gói từng service và chạy các profile của toàn hệ thống |
| Operational source | PostgreSQL | Relational database nguồn duy nhất của MVP |
| Sinh dữ liệu | Faker, SQLAlchemy, APScheduler | Sinh và ghi dữ liệu mô phỏng theo các chu kỳ khác nhau |
| Batch ingestion | Python, SQLAlchemy, PyArrow | Đọc incremental từ PostgreSQL và xử lý dữ liệu batch |
| Object storage | MinIO | S3-compatible object storage chạy local |
| Physical file format | Apache Parquet | Định dạng lưu trữ dữ liệu chính |
| Lakehouse table format | Apache Iceberg | Snapshot, time travel, schema/partition evolution và row-level changes |
| Iceberg Python client | PyIceberg | Tương tác với Iceberg bằng Python |
| Iceberg catalog | Project Nessie | Catalog đầu tiên cho Iceberg; cần xác thực compatibility trong PoC |
| SQL query engine | Trino | Truy vấn Iceberg và các nguồn liên quan bằng SQL |
| SQL transformation | dbt Core, dbt-trino | Xây dựng staging, intermediate, fact, dimension và data marts |
| Orchestration | Apache Airflow | Scheduling, dependency, retry, backfill và vận hành batch workflow |
| Data quality | Great Expectations | Kiểm tra chất lượng tại ingestion và giữa các stage |
| Business/model tests | dbt tests | Kiểm tra uniqueness, relationship, accepted values và business rules |
| Metadata và lineage | OpenMetadata | Discovery, ownership, metadata catalog và lineage |
| Metrics | Prometheus | Thu thập metrics của platform và service |
| Operational dashboard | Grafana | Trực quan hóa metrics và tình trạng hệ thống |
| Centralized logging | Grafana Loki, Grafana Alloy | Thu thập và truy vấn container/application logs |
| Alerting | Prometheus Alertmanager | Nhóm, định tuyến và quản lý cảnh báo |
| BI | Power BI Desktop miễn phí | Xây dựng dashboard trong máy ảo Windows |
| BI serving layer | PostgreSQL analytics mart | Điểm kết nối ổn định giữa Power BI và dữ liệu đã curated |
| Integration testing | pytest, Testcontainers | Kiểm thử tích hợp bằng container cô lập và synthetic fixture |
| Configuration validation | YAML, Pydantic | Chọn implementation và từ chối tổ hợp cấu hình không hợp lệ |

### Luồng dữ liệu baseline

```text
Faker + SQLAlchemy + APScheduler
                │
                ▼
           PostgreSQL
                │
                ▼
Python + SQLAlchemy + PyArrow
                │
                ▼
MinIO + Parquet + Iceberg + Nessie
                │
                ▼
              Trino
                │
                ▼
       dbt Core + dbt-trino
                │
                ▼
    PostgreSQL analytics mart
                │
                ▼
       Power BI Desktop (VM)
```

Airflow điều phối luồng batch. Great Expectations và dbt tests kiểm soát chất lượng. OpenMetadata thu thập metadata và lineage. Prometheus, Grafana, Loki/Alloy và Alertmanager cung cấp observability.

### Lý do cho BI serving layer

Power BI không kết nối trực tiếp vào lakehouse trong baseline. Curated marts được publish sang PostgreSQL để Power BI sử dụng connector PostgreSQL chính thức, hỗ trợ Import và DirectQuery. Cách này giữ đường kết nối miễn phí và ổn định trong Windows VM, đồng thời tránh đưa driver Trino của bên thứ ba vào critical path của MVP.

Tham khảo: [Power Query PostgreSQL connector](https://learn.microsoft.com/en-us/power-query/connectors/postgresql).

### Compatibility cần được xác thực

Trino là query engine chính vì Iceberg connector hỗ trợ đọc/ghi Iceberg, Parquet, MinIO/S3-compatible storage và nhiều catalog implementation. Tuy nhiên phiên bản cụ thể của Trino, Iceberg, Nessie, PyIceberg và dbt-trino phải được kiểm tra bằng compatibility matrix và PoC trước khi pin dependency.

Tham khảo:

- [Trino Iceberg connector](https://trino.io/docs/current/connector/iceberg.html)
- [Apache Iceberg REST Catalog specification](https://iceberg.apache.org/rest-catalog-spec/)

### Compose profiles dự kiến

| Profile | Thành phần chính |
|---|---|
| `source` | PostgreSQL nguồn và data generator |
| `core` | MinIO, Nessie và Trino |
| `batch` | Airflow, batch ingestion, dbt và Great Expectations |
| `catalog` | OpenMetadata và các dependency bắt buộc |
| `observability` | Prometheus, Grafana, Loki/Alloy và Alertmanager |
| `bi` | PostgreSQL analytics mart phục vụ Power BI |
| `cdc` | Placeholder cho CDC stack ở phase sau |
| `full` | Tập hợp các profile cần cho demo end-to-end |

`full` không có nghĩa mọi technology implementation thay đều phải chạy đồng thời. Cấu hình lựa chọn implementation và Compose profile là hai cơ chế độc lập.

## Công nghệ chỉ chuẩn bị kiến trúc trong MVP

Các công nghệ sau không nằm trong critical path triển khai đầu tiên:

| Capability tương lai | Công nghệ dự kiến |
|---|---|
| CDC từ PostgreSQL | Debezium |
| Event streaming | Apache Kafka |
| Schema registry | Apicurio Registry |
| Streaming processing | Apache Flink |
| Distributed batch processing | Apache Spark |
| Security/identity | Keycloak |
| Secrets management | OpenBao hoặc HashiCorp Vault Community tùy kết quả đánh giá license và vận hành |

Kiến trúc cần chừa boundary để bổ sung các capability này nhưng không triển khai chúng trong milestone batch đầu tiên.

## Nhóm công nghệ thay thế để nghiên cứu sau

| Capability | Baseline | Implementation thay thế dự kiến |
|---|---|---|
| Table format | Apache Iceberg | Delta Lake |
| Object storage | MinIO | LocalStack S3 hoặc Ceph |
| Catalog | Project Nessie | Apache Polaris, Lakekeeper hoặc JDBC Catalog |
| Orchestration | Apache Airflow | Dagster hoặc Prefect |
| Query engine | Trino | DuckDB, Spark SQL hoặc Dremio Community nếu đáp ứng license |
| Data quality | Great Expectations | Soda Core hoặc custom dbt tests |
| Metadata/lineage | OpenMetadata | DataHub |
| BI | Power BI Desktop | Apache Superset hoặc Metabase |

Implementation thay thế phải dùng cùng data contract, synthetic dataset, integration tests và acceptance criteria với baseline.

## Mục tiêu

- Xác định các yêu cầu làm cơ sở lựa chọn công nghệ.
- So sánh những phương án phù hợp cho từng lớp của data platform.
- Đề xuất technology stack cho MVP và hướng phát triển production.
- Làm rõ trade-off, chi phí, rủi ro và các điều kiện cần xác nhận.
- Cung cấp đủ cơ sở để chủ dự án phê duyệt trước khi tạo ADR và triển khai.

## Phạm vi nghiên cứu

Báo cáo cần đánh giá các lớp sau:

- Nguồn dữ liệu mẫu và source simulation.
- Batch ingestion và nhu cầu streaming trong tương lai.
- Object storage, data lake hoặc lakehouse.
- Data processing và transformation.
- Data modeling và semantic layer.
- Workflow orchestration.
- Data quality và data contracts.
- Metadata catalog và data lineage.
- Query engine hoặc data warehouse.
- BI, reporting và data products.
- Monitoring, logging và alerting.
- Security, secrets và access control.
- Testing, local development và CI/CD.
- Phương án triển khai local, on-premise và cloud.

Việc đánh giá cloud trong task này chỉ nhằm xác định đường mở rộng tương lai. Recommendation cho MVP phải ưu tiên local và Docker.

## Nguyên tắc kiến trúc cần đánh giá

- Xác định interface, data contract và boundary ổn định giữa các lớp trước khi chọn implementation.
- Mỗi capability có thể có nhiều implementation trong cùng codebase nhưng tại một thời điểm chỉ kích hoạt implementation được chọn bằng cấu hình.
- Tách cấu hình đặc thù công nghệ khỏi business logic và data contract khi có thể.
- Dùng cùng dataset, workload và acceptance criteria để so sánh các công nghệ thay thế.
- Không giả định hai công nghệ cùng loại có semantics hoặc feature set hoàn toàn tương đương.
- Ghi rõ migration path, compatibility và chi phí chuyển đổi giữa các implementation.
- Giữ schema nguồn độc lập với mô hình dữ liệu lakehouse.
- Cấu hình lựa chọn công nghệ phải được validate và từ chối các tổ hợp không tương thích.
- Compose profile quản lý nhóm service chạy cùng nhau; file lựa chọn implementation quản lý công nghệ được dùng cho từng capability. Hai cơ chế phải có trách nhiệm tách biệt.

## Ngoài phạm vi

- Cài đặt hoặc cấu hình công nghệ được đề xuất.
- Tạo hoặc sửa production code.
- Thay đổi dependency, runtime configuration, IaC hoặc CI/CD.
- Chạy deployment, migration, backfill hoặc data pipeline.
- Chốt cloud provider khi chưa có đủ yêu cầu và ràng buộc.

## Phương pháp đánh giá

1. Thu thập và ghi rõ các giả định về quy mô dữ liệu, tần suất cập nhật, SLA, ngân sách và năng lực vận hành.
2. Xác định tiêu chí đánh giá và trọng số trước khi chấm điểm.
3. Chọn ít nhất hai phương án khả thi cho mỗi quyết định quan trọng.
4. So sánh bằng cùng một bộ tiêu chí và giải thích cơ sở chấm điểm.
5. Tách biệt stack local-first cho MVP với kiến trúc production mục tiêu.
6. Ghi nhận các câu hỏi mở dưới dạng decision gate, không tự suy đoán để chốt lựa chọn.
7. Sử dụng tài liệu chính thức cho các thông tin kỹ thuật có khả năng thay đổi.
8. Xây dựng capability matrix để phân nhóm các công nghệ có thể thay thế lẫn nhau.
9. Đề xuất benchmark hoặc proof-of-concept dùng chung cho các implementation trong từng nhóm.
10. Đề xuất cấu trúc plugin/adapter và configuration schema cho nhiều implementation cùng tồn tại, nhưng không triển khai trong phạm vi task này.

## Tiêu chí đánh giá tối thiểu

- Mức độ phù hợp với mục tiêu và use case FMCG.
- Khả năng chạy local và tái tạo môi trường.
- Độ phức tạp khi phát triển và vận hành.
- Khả năng mở rộng về dữ liệu và workload.
- Data quality, observability và khả năng truy vết.
- Tính tích hợp giữa các thành phần.
- Mức độ trưởng thành của hệ sinh thái và cộng đồng.
- Chi phí hạ tầng, license và vận hành tương đối.
- Yêu cầu kỹ năng của đội ngũ.
- Rủi ro vendor lock-in và khả năng thay thế.
- Security và governance.
- Mức độ phù hợp cho học tập, demo và portfolio.
- Khả năng chạy ổn định bằng Docker trên môi trường local.
- Chất lượng Python SDK, API hoặc ecosystem liên quan.
- Mức độ tương thích với Parquet và kiến trúc lakehouse.
- Khả năng thay thế implementation mà không làm thay đổi data contract cốt lõi.

Trọng số chính thức phải được đề xuất trong báo cáo và cần chủ dự án xác nhận trước khi dùng để chốt stack.

## Deliverables

- Báo cáo đánh giá technology stack bằng Markdown.
- Bảng so sánh các phương án theo tiêu chí có trọng số.
- Stack khuyến nghị cho MVP, kèm lý do và các lựa chọn thay thế.
- Hướng phát triển từ local-first lên production.
- Danh sách trade-off, rủi ro và biện pháp giảm thiểu.
- Danh sách decision gate và câu hỏi cần chủ dự án xác nhận.
- Đề xuất các ADR cần tạo sau khi stack được phê duyệt.
- Danh sách nguồn tham khảo chính thức.
- Capability matrix thể hiện các nhóm công nghệ có thể hoán đổi.
- Đề xuất bộ kiểm thử so sánh chung, cấu trúc adapter và configuration schema cho từng technology experiment.
- Đề xuất Compose profiles tối thiểu: `core`, `batch`, `cdc`, `catalog`, `observability`, `bi` và `full`, đồng thời đánh giá dependency giữa các profile.

## Tiêu chí nghiệm thu

- [ ] Các giả định và yêu cầu đầu vào được ghi rõ.
- [ ] Mọi lớp công nghệ trong phạm vi đều được đánh giá.
- [ ] Có ít nhất hai phương án cho mỗi quyết định quan trọng.
- [ ] Tiêu chí, trọng số và cơ sở chấm điểm được giải thích.
- [ ] Có recommendation rõ ràng cho MVP và production direction.
- [ ] Trade-off, chi phí tương đối và rủi ro vendor lock-in được trình bày.
- [ ] Các câu hỏi chưa đủ dữ liệu được ghi nhận, không bị biến thành giả định ngầm.
- [ ] Các claim có thể thay đổi theo thời gian có link đến tài liệu chính thức.
- [ ] Không có production code hoặc cấu hình runtime nào bị thay đổi.
- [ ] Chủ dự án đã review và phê duyệt kết luận trước khi tạo ADR.
- [ ] Recommendation có thể chạy local, đóng gói bằng Docker và ưu tiên Python.
- [ ] Operational database được xem là nguồn dữ liệu duy nhất của MVP.
- [ ] Kiến trúc đề xuất sử dụng lakehouse và Parquet làm nền tảng lưu trữ chính.
- [ ] Các công nghệ thay thế được phân nhóm theo capability và có tiêu chí so sánh chung.
- [ ] Tổng memory limit của stack không vượt quá ngân sách RAM khoảng 36 GB trong profile mặc định.
- [ ] Stack đầu tiên sử dụng PostgreSQL, MinIO và Apache Iceberg, trừ khi báo cáo chứng minh có blocker kỹ thuật.
- [ ] Power BI có đường kết nối được mô tả và kiểm chứng về mặt kiến trúc.
- [ ] Root Compose có thể tổng hợp các Compose file của từng service mà không sao chép cấu hình service.
- [ ] Batch pipeline được xác định là implementation đầu tiên; CDC có extension path rõ ràng.
- [ ] Distributed processing và security nâng cao không bị đưa vào critical path của MVP.
- [ ] Configuration schema có thể lựa chọn implementation và phát hiện tổ hợp công nghệ không tương thích.
- [ ] Compose profiles cho phép chạy từng nhóm service mà không yêu cầu toàn bộ stack cùng hoạt động.

## Files dự kiến thay đổi

- `docs/task-reports/2026/09/02/TASK-003-technology-stack-selection.md`
- File báo cáo kết quả sẽ được xác định khi task bắt đầu.
- Các ADR chỉ được tạo sau khi recommendation được chủ dự án phê duyệt.

## Rủi ro

- Chọn công nghệ quá sớm khi chưa biết quy mô dữ liệu và SLA.
- Thiết kế quá phức tạp so với nhu cầu của MVP.
- Đánh đồng stack dùng để học tập với stack production của doanh nghiệp.
- Tạo nhiều thành phần trùng chức năng và tăng chi phí vận hành.
- Khóa chặt vào một nhà cung cấp trước khi có business requirement.
- Coi các table format hoặc storage implementation là tương đương dù có khác biệt về semantics và tính năng.
- Để logic đặc thù công nghệ lan sang các lớp khác, làm tăng chi phí thay thế.
- Nhiều implementation trên cùng nhánh có thể làm tăng dependency, kích thước image và độ phức tạp cấu hình.
- File lựa chọn công nghệ có thể tạo ra các tổ hợp không tương thích nếu thiếu schema validation và compatibility matrix.

## Nội dung không dùng làm tiêu chí chặn

- Hệ điều hành host, kiến trúc CPU và dung lượng SSD không được dùng làm điều kiện chặn cho lựa chọn ban đầu.
- Chưa cần đặt con số benchmark hiệu năng cụ thể ngoài khả năng xử lý dataset MVP vài nghìn dòng.
- Không yêu cầu toàn bộ stack chạy đồng thời trong ngân sách RAM khoảng 36 GB.

## Câu hỏi còn cần xác nhận trong quá trình nghiên cứu

- Power BI nên kết nối trực tiếp tới query engine nào và driver/giao thức nào phù hợp nhất?
- Configuration schema nên chọn implementation ở cấp capability hay chọn một preset stack hoàn chỉnh?
- Những tổ hợp implementation nào được hỗ trợ chính thức và tổ hợp nào phải bị từ chối?
- Ranh giới giữa service Compose riêng, root Compose và profile nên được thiết kế thế nào để tránh lặp cấu hình?

Các câu hỏi này là nội dung task phải phân tích và đề xuất, không yêu cầu thêm câu trả lời đầu vào từ chủ dự án trước khi bắt đầu báo cáo.

## Kết quả mong đợi

Một recommendation có căn cứ, đủ đơn giản để triển khai MVP nhưng vẫn thể hiện được con đường mở rộng lên môi trường production. Báo cáo là đầu vào cho quá trình review của chủ dự án, không tự động trở thành quyết định kiến trúc.
