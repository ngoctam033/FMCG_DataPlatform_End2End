# TASK-006 — Lập kế hoạch codebase cho Modular Compose

## Thông tin

- Ngày tạo: 2026-09-02
- Ngày thực hiện: 2026-09-02
- Trạng thái: Planned
- Người thực hiện: Chưa phân công
- Parent task: Không có
- Task/Issue: Thiết kế các codebase con và cơ chế tổng hợp Docker Compose

## Bối cảnh

Repository đang sử dụng mô hình monorepo và đã có các khu vực theo capability như `ingestion/`, `transformation/`, `orchestration/`, `quality/` và `analytics/`. Khu vực `services/` hiện chứa `data-source-simulators/` theo hướng source-system-first.

Technology baseline của MVP gồm PostgreSQL, MinIO, Apache Iceberg, Project Nessie, Trino, dbt Core, Apache Airflow, Great Expectations, OpenMetadata, Prometheus, Grafana, Loki/Alloy, Alertmanager và PostgreSQL analytics mart. Mỗi deployable unit cần chạy độc lập; root repository cần có khả năng tổng hợp các Compose application thành một hệ thống.

Task này chỉ lập kế hoạch kiến trúc codebase và runtime configuration. Không tạo hoặc sửa Docker Compose, Dockerfile, executable code, dependency hay cấu hình runtime.

## Hiện trạng codebase

```text
.
├── analytics/
├── config/
├── contracts/
├── data/
├── docs/
├── infrastructure/
├── ingestion/
├── orchestration/
├── quality/
├── scripts/
├── services/
│   └── data-source-simulators/
│       ├── shared/
│       └── simple-generators/
├── src/
├── tests/
└── transformation/
```

### Nhận xét

- Các thư mục top-level mô tả capability hoặc loại artifact, không phải tất cả đều là service có thể deploy.
- `services/data-source-simulators/` đã có boundary rõ và cần được giữ nguyên.
- Chưa có khu vực tập trung cho các platform service của lakehouse.
- Chưa có convention thống nhất về vị trí `compose.yaml`, `.env.example`, cấu hình service và persistent data.
- Chưa có root composition model.
- Có xung đột task ID: hai file đang sử dụng `TASK-003`. Task này chỉ ghi nhận, không tự đổi tên tài liệu lịch sử.

## Quyết định tổ chức đề xuất

### 1. Phân biệt source code và deployable unit

- Các khu vực top-level như `ingestion/`, `transformation/`, `quality/` tiếp tục sở hữu source artifact theo capability.
- `services/` sở hữu các application hoặc infrastructure component có vòng đời container độc lập.
- Không di chuyển production file hiện có trong task cấu trúc.
- Một service chỉ được tạo khi có follow-up task và owner rõ ràng.

### 2. Mỗi service tự sở hữu deployment boundary

Convention dự kiến cho service cần build image:

```text
services/<group>/<service>/
├── README.md
├── app/                       # Chỉ tạo khi có implementation được duyệt
├── config/                    # Non-secret service configuration
├── deployment/
│   ├── compose.yaml
│   └── .env.example
└── tests/                     # Chỉ tạo khi task yêu cầu test rõ ràng
```

Convention dự kiến cho third-party service chỉ dùng official image:

```text
services/<group>/<service>/
├── README.md
├── config/
└── deployment/
    ├── compose.yaml
    └── .env.example
```

Không tạo Dockerfile nếu official image đáp ứng yêu cầu và không có customization.

### 3. Root Compose chỉ làm composition

Root `compose.yaml` dự kiến sử dụng Compose `include` để nạp Compose application của từng service. Root file không sao chép lại image, port, volume, healthcheck hoặc environment của service con.

Lý do chọn `include` thay cho chuỗi `-f`:

- Mỗi Compose con giữ project directory riêng để relative path được resolve theo vị trí của nó.
- Phù hợp monorepo có nhiều sub-domain sở hữu Compose riêng.
- Xung đột resource name được phát hiện thay vì âm thầm merge.
- Yêu cầu Docker Compose 2.20.0 trở lên phải được ghi thành prerequisite.

Tham khảo: [Docker Compose `include`](https://docs.docker.com/reference/compose-file/include/) và [Use multiple Compose files](https://docs.docker.com/compose/how-tos/multiple-compose-files/).

### 4. Phân biệt `include`, `profiles` và technology selector

| Cơ chế | Trách nhiệm |
|---|---|
| Compose `include` | Tổng hợp service-owned Compose application vào root application |
| Compose `profiles` | Bật hoặc tắt nhóm service theo use case vận hành |
| Technology selector | Chọn implementation cho từng capability và kiểm tra compatibility |

Không dùng profile làm technology selector duy nhất. Ví dụ `batch` mô tả workload cần chạy, còn cấu hình implementation quyết định catalog là Nessie hay Polaris.

## Cấu trúc codebase mục tiêu

```text
.
├── compose.yaml                         # Root composition; tạo ở task được cấp quyền
├── config/
│   ├── stacks/                          # Preset stack được hỗ trợ
│   ├── compatibility/                   # Compatibility matrix/schema
│   └── environments/                    # Local non-secret overrides
├── contracts/
├── services/
│   ├── data-source-simulators/
│   │   ├── simple-generators/
│   │   ├── shared/
│   │   └── odoo-erp/                    # Chỉ tạo theo TASK-005 khi được duyệt
│   ├── ingestion/
│   │   ├── batch-ingestion/
│   │   └── cdc/                         # Placeholder/future phase, chưa triển khai
│   ├── lakehouse/
│   │   ├── minio/
│   │   ├── iceberg-catalog-nessie/
│   │   └── iceberg-writer/
│   ├── query/
│   │   └── trino/
│   ├── transformation/
│   │   └── dbt-trino/
│   ├── orchestration/
│   │   └── airflow/
│   ├── quality/
│   │   └── great-expectations/
│   ├── metadata/
│   │   └── openmetadata/
│   ├── observability/
│   │   ├── prometheus/
│   │   ├── grafana/
│   │   ├── loki/
│   │   ├── alloy/
│   │   └── alertmanager/
│   └── serving/
│       └── analytics-postgres/
├── ingestion/                           # Source artifacts owned by ingestion capability
├── transformation/                      # dbt/model source artifacts nếu tách khỏi wrapper service
├── orchestration/                       # DAG source artifacts nếu tách khỏi Airflow wrapper
├── quality/                             # Quality suites và business tests
├── analytics/                           # Power BI project và analytics artifacts
└── tests/                               # Cross-service integration/contract/E2E tests
```

## Boundary cần giữ rõ

| Khu vực | Sở hữu | Không sở hữu |
|---|---|---|
| `services/**` | Container boundary, service config và deployment wrapper | Cross-platform business contract |
| `contracts/**` | Versioned interface giữa producer và consumer | Runtime implementation |
| `ingestion/**` | Batch/CDC connector source code | Source simulator hoặc storage service config |
| `transformation/**` | dbt project và transformation models | Trino/MinIO deployment |
| `orchestration/**` | DAG definitions | Airflow platform deployment |
| `quality/**` | Quality rules và validation suites | Great Expectations platform wrapper nếu có |
| `analytics/**` | Power BI project và semantic/report artifacts | Analytics PostgreSQL deployment |
| `infrastructure/**` | Shared deployment policy và future IaC | Business logic |

Nếu một framework chỉ là runtime cho artifact top-level, service wrapper nên mount hoặc package artifact đó thay vì tạo bản sao. Ví dụ Airflow service sử dụng DAG từ `orchestration/`; dbt runner sử dụng project từ `transformation/`.

## Compose ownership và naming convention

### File ownership

- Root: `/compose.yaml` — chỉ include và root-level documentation.
- Service: `services/<group>/<service>/deployment/compose.yaml`.
- Service defaults: `services/<group>/<service>/deployment/.env.example`.
- Secret/local override: `.env` không commit.
- Third-party configuration: `services/<group>/<service>/config/`.

### Resource naming

- Service name: `<group>-<service>`, ví dụ `lakehouse-minio`, `query-trino`.
- Named volume: `fmcg_<service>_<purpose>`, ví dụ `fmcg_minio_data`.
- Internal network theo trust/data-flow boundary, không tạo một network toàn cục nếu không cần.
- Host port chỉ publish cho UI, API hoặc BI connection cần truy cập từ host/Windows VM.
- Internal database port không publish mặc định.

Tên cuối cùng cần được chuẩn hóa trong một standard riêng trước khi tạo Compose.

## Compose profiles đề xuất

| Profile | Service/capability chính | Ghi chú |
|---|---|---|
| `source` | Source database và data generator | Odoo có thể có sub-profile riêng |
| `core` | MinIO, Nessie, Trino | Lakehouse query path tối thiểu |
| `batch` | Batch ingestion, Airflow, dbt, GX | MVP đầu tiên |
| `catalog` | OpenMetadata và dependency | Chạy khi cần catalog/lineage |
| `observability` | Prometheus, Grafana, Loki, Alloy, Alertmanager | Có thể bật độc lập khi debug |
| `bi` | Analytics PostgreSQL | Power BI chạy ngoài Docker trong Windows VM |
| `cdc` | Debezium, Kafka, registry | Future phase |
| `full` | Preset demo end-to-end | Không đồng nghĩa mọi implementation thay thế cùng chạy |

Docker Compose profiles cho phép bật nhiều nhóm service bằng nhiều `--profile` hoặc `COMPOSE_PROFILES`. Service không gán profile sẽ luôn được bật, vì vậy root design nên hạn chế service unprofiled ngoài dependency thật sự bắt buộc. Tham khảo: [Docker Compose profiles](https://docs.docker.com/compose/how-tos/profiles/).

## Dependency graph dự kiến

```text
source
  └──► batch
          ├──► core
          ├──► catalog
          └──► observability

core
  ├── MinIO
  ├── Nessie
  └── Trino

bi
  ├── analytics-postgres
  └── Power BI Desktop (external Windows VM)

cdc (future)
  └──► source + core
```

Compose `depends_on` chỉ mô tả dependency trong cùng application model và không thay thế readiness contract. Mỗi service có dependency runtime phải có healthcheck/readiness strategy riêng.

## Thứ tự tạo codebase con

### Milestone 0 — Standards và root contract

1. Xử lý xung đột task ID hiện có bằng task quản trị riêng.
2. Tạo standard cho service naming, ports, volumes, networks, environment variables và healthchecks.
3. Định nghĩa technology selector schema và compatibility matrix ở mức tài liệu.
4. Xác nhận Docker Compose tối thiểu là 2.20.0 để dùng `include`.

### Milestone 1 — Source

1. Thực hiện `TASK-005` cho `odoo-erp/` sau khi có approval runtime rõ ràng, hoặc chọn simple generator làm source đầu tiên.
2. Mỗi source system có Compose độc lập.
3. Không đặt source database của Odoo trùng với analytics PostgreSQL.

### Milestone 2 — Core lakehouse

1. Tạo `services/lakehouse/minio/`.
2. Tạo `services/lakehouse/iceberg-catalog-nessie/`.
3. Tạo `services/query/trino/`.
4. Tạo integration contract cho MinIO–Nessie–Trino trước khi thêm writer.

### Milestone 3 — Batch path

1. Tạo `services/ingestion/batch-ingestion/`.
2. Tạo `services/lakehouse/iceberg-writer/` nếu writer có vòng đời container riêng; nếu không, giữ writer trong batch-ingestion package.
3. Tạo `services/transformation/dbt-trino/` làm deployment wrapper cho project trong `transformation/`.
4. Tạo `services/orchestration/airflow/` làm deployment wrapper cho DAG trong `orchestration/`.
5. Tạo `services/quality/great-expectations/` chỉ khi GX cần runner/container độc lập.

### Milestone 4 — BI serving

1. Tạo `services/serving/analytics-postgres/`.
2. Định nghĩa publish boundary từ curated Iceberg mart sang serving database.
3. Lưu Power BI project trong `analytics/power-bi/`, không trong `services/` vì Power BI chạy ngoài Docker.

### Milestone 5 — Catalog và observability

1. Tạo OpenMetadata wrapper và profile `catalog`.
2. Tạo observability service folders.
3. Bật từng component theo nhu cầu; không bắt buộc chạy toàn bộ khi phát triển pipeline.

### Milestone 6 — Root composition

1. Tạo root `compose.yaml` chỉ sau khi ít nhất một Compose con đã hợp lệ.
2. Include từng Compose con bằng đường dẫn tương đối.
3. Validate resolved model bằng `docker compose config`.
4. Kiểm tra duplicate service, volume, network và port names.
5. Chứng minh service con chạy độc lập trước khi kiểm tra profile end-to-end.

## Follow-up tasks đề xuất

| Thứ tự | Task | Phạm vi |
|---|---|---|
| 1 | Compose standards | Naming, ownership, port, network, volume, healthcheck |
| 2 | Technology selector design | Schema, preset và compatibility matrix |
| 3 | MinIO service wrapper | Folder, Compose, config và smoke test |
| 4 | Nessie service wrapper | Folder, Compose, catalog config và smoke test |
| 5 | Trino service wrapper | Folder, Compose, catalog properties và query smoke test |
| 6 | Root Compose core | Include ba service core và validate model |
| 7 | Batch ingestion service | PostgreSQL-to-Iceberg batch boundary |
| 8 | Airflow deployment wrapper | Orchestrate batch path |
| 9 | dbt-trino deployment wrapper | SQL transformations và model tests |
| 10 | Analytics PostgreSQL | BI serving boundary |
| 11 | Observability stack | Metrics, logs, dashboard và alerting |
| 12 | OpenMetadata stack | Metadata ingestion và lineage |

Mỗi task tạo runtime configuration phải có approval ngoại lệ rõ ràng theo `AGENTS.md`. Không gộp toàn bộ danh sách vào một task triển khai lớn.

## Tiêu chí nghiệm thu cho kế hoạch

- [x] Hiện trạng và ranh giới codebase được phân tích.
- [x] Có cây thư mục mục tiêu cho các codebase con.
- [x] Phân biệt source artifact và deployable service.
- [x] Xác định trách nhiệm của root Compose và service Compose.
- [x] Phân biệt `include`, profile và technology selector.
- [x] Có profile, dependency graph và thứ tự triển khai.
- [x] Có follow-up task nhỏ, có thể review độc lập.
- [x] Không tạo hoặc sửa runtime configuration.
- [x] Không tạo executable code hoặc dependency.

## Files changed

- `docs/task-reports/2026/09/02/TASK-006-modular-compose-codebase-plan.md`

## Rủi ro

- Tạo service folder cho từng tool có thể dẫn tới quá nhiều wrapper không cần thiết.
- Nhiều Compose file có thể xung đột service, network, volume hoặc port name.
- Đưa source artifact vào cả top-level capability và service wrapper có thể gây duplication.
- `include` yêu cầu Docker Compose 2.20.0 trở lên.
- Profile và `depends_on` phức tạp có thể khiến hành vi khởi động khó đoán nếu dependency không được ghi rõ.
- Technology selector có thể tạo tổ hợp không tương thích nếu thiếu validation.

## Rollback

Task hiện tại chỉ thêm tài liệu Markdown và không tác động runtime. Có thể rollback bằng cách hoàn tác file kế hoạch này sau khi chủ dự án review. Các follow-up task phải có rollback riêng cho container, network và volume; không được xóa named volume nếu chưa được phê duyệt.

## Kết luận

Giữ cấu trúc capability hiện tại cho source artifact, mở rộng `services/` theo deployable unit và để mỗi service sở hữu Compose riêng. Root Compose sử dụng `include` để tổng hợp, profiles để chọn nhóm workload, và một technology selector độc lập để chọn implementation. Bắt đầu từ `source` và `core`, sau đó hoàn thiện đường batch trước khi bổ sung catalog, observability và CDC.

