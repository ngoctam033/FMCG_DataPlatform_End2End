# Data Contracts

Thư mục này chứa các data contract - định nghĩa giao diện, schema, event format, API spec và file format dùng để trao đổi dữ liệu giữa các Data Source Simulators và hệ thống Ingestion.

## Trách nhiệm

- Định nghĩa schema rõ ràng cho từng miền dữ liệu.
- Làm tài liệu tham chiếu (source of truth) về hình dạng dữ liệu cho cả bên cung cấp (simulator) và bên tiêu thụ (ingestion).
- Quản lý version của schema khi có sự thay đổi.

## Các loại Contract

- `api/`: OpenAPI specs, GraphQL schemas, gRPC protobufs.
- `database/`: Schema định nghĩa table, view (ví dụ: cho CDC hoặc database replica).
- `events/`: AsyncAPI specs, Avro/JSON schemas dùng cho Kafka/Event Streams.
- `files/`: Định dạng file CSV, Parquet, JSON, v.v. trao đổi qua batch.
