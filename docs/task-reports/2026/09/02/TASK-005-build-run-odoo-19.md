# TASK-005 — Build và chạy Odoo 19 nguyên bản

## Thông tin

- Ngày tạo: 2026-09-02
- Ngày thực hiện: Chưa thực hiện
- Trạng thái: Planned
- Người thực hiện: Chưa phân công
- Parent task: Không có
- Task/Issue: TASK-005

## Bối cảnh

FMCG Data Platform cần một ERP source system giả lập có khả năng mở rộng thành nguồn dữ liệu hoàn chỉnh trong tương lai. Odoo 19 được chọn làm ERP simulator đầu tiên và phải nằm độc lập, ngang hàng với `simple-generators/`, trong codebase `data-source-simulators`.

Odoo 19 có Docker Official Image với tag `19.0` và cần PostgreSQL để vận hành. Tài liệu Odoo 19 quy định PostgreSQL 13 trở lên. Giai đoạn này chỉ cần dựng môi trường local bằng Docker Compose, khởi động được Odoo nguyên bản và tạo database thử nghiệm; chưa phát triển custom module hoặc logic sinh dữ liệu FMCG.

## Mục tiêu

- Bổ sung Odoo 19 như một source system độc lập tại `services/data-source-simulators/odoo-erp/`.
- Cung cấp cấu hình Docker Compose để chạy Odoo 19 cùng PostgreSQL trong môi trường local.
- Đảm bảo dữ liệu Odoo và PostgreSQL được lưu bằng named volume qua các lần restart.
- Cung cấp hướng dẫn setup, khởi động, kiểm tra, dừng và reset môi trường.
- Giữ nguyên Odoo tiêu chuẩn, không custom module, source code hoặc business flow.

## Phạm vi triển khai

- Sử dụng Docker Official Image `odoo:19.0`.
- Sử dụng PostgreSQL phiên bản tương thích với Odoo 19; version cụ thể phải được pin trong Compose sau khi xác nhận theo tài liệu chính thức.
- Tạo Docker Compose stack gồm tối thiểu:
  - Odoo 19 service.
  - PostgreSQL service.
  - Named volume cho Odoo filestore.
  - Named volume cho PostgreSQL data.
  - Healthcheck hoặc readiness check phù hợp.
  - Network nội bộ dành cho Odoo và PostgreSQL.
- Chỉ publish cổng Odoo cần thiết cho local development; không publish cổng PostgreSQL nếu không có nhu cầu đã được phê duyệt.
- Tạo `.env.example` chỉ chứa giá trị mẫu không nhạy cảm.
- Bảo đảm credential thật và file `.env` không được commit.
- Viết README hướng dẫn thao tác và cảnh báo rõ đây là môi trường local/simulator, không phải production deployment.
- Cập nhật README của `data-source-simulators` và README cấp repository để ghi nhận Odoo ERP simulator.

## Cấu trúc dự kiến

```text
services/
└── data-source-simulators/
    ├── README.md
    ├── simple-generators/
    ├── shared/
    └── odoo-erp/
        ├── README.md
        ├── .env.example
        └── deployment/
            └── compose.yaml
```

Không tạo `app/`, `addons/`, `seed/`, `scenarios/` hoặc `exports/` trong task này vì chưa có customization hay data-generation logic tương ứng.

## Ngoài phạm vi

- Phát triển hoặc cài đặt custom Odoo module.
- Tùy chỉnh source code, giao diện hoặc business logic của Odoo.
- Tạo dữ liệu seed FMCG hoặc tự động hóa giao dịch ERP.
- Cấu hình CDC, API extraction, batch export hoặc ingestion connector.
- Tích hợp Kafka, webhook hoặc message broker.
- Cài đặt Odoo Enterprise hoặc sử dụng subscription code.
- Thiết lập HTTPS, reverse proxy, public domain hoặc internet-facing deployment.
- Hardening cho production, high availability, backup production hoặc disaster recovery.
- Kết nối tới database, credential hoặc dữ liệu production.
- Chạy `docker compose down --volumes` nếu chưa có xác nhận rõ ràng vì thao tác này xóa dữ liệu local đã lưu.

## Deliverables

- Thư mục `services/data-source-simulators/odoo-erp/` có ranh giới trách nhiệm rõ ràng.
- Docker Compose configuration cho Odoo 19 và PostgreSQL.
- File biến môi trường mẫu không chứa secret thật.
- Named volumes cho filestore và database.
- README hướng dẫn đầy đủ vòng đời local environment.
- Bằng chứng kiểm tra Odoo truy cập được trên cổng local được cấu hình.
- Báo cáo kết quả và các lệnh kiểm tra đã thực hiện trong task report này.

## Files dự kiến thay đổi

- `README.md`
- `.gitignore` nếu cần bổ sung loại trừ credential hoặc local artifact cụ thể của Odoo
- `services/data-source-simulators/README.md`
- `services/data-source-simulators/odoo-erp/README.md`
- `services/data-source-simulators/odoo-erp/.env.example`
- `services/data-source-simulators/odoo-erp/deployment/compose.yaml`
- `docs/task-reports/2026/09/02/TASK-005-build-run-odoo-19.md`

## Quyết định kỹ thuật

- Đặt Odoo tại `services/data-source-simulators/odoo-erp/` vì Odoo đóng vai một source system hoàn chỉnh, không phải ingestion component hoặc một business domain đơn lẻ.
- Dùng Docker Compose cho môi trường local gồm Odoo và PostgreSQL.
- Dùng trực tiếp Docker Official Image `odoo:19.0`; không tạo Dockerfile chỉ để kế thừa cùng image khi chưa có customization.
- Không dùng tag `latest` để tránh tự động chuyển major/minor version ngoài kiểm soát.
- Database và filestore phải dùng named volume để tồn tại qua `stop`, `down` và restart thông thường.
- Cấu hình ở task này chỉ phục vụ local simulator và không được xem là production-ready.

## Quyền thực thi và approval gate

Task này dự kiến tạo runtime configuration và khởi chạy container, là các hành động bị giới hạn theo `AGENTS.md`. Việc tạo task report không tự động cấp quyền triển khai.

Trước khi thực hiện task, chủ dự án phải cho phép rõ ràng:

- Tạo hoặc sửa đúng các file runtime configuration được liệt kê trong phạm vi task.
- Pull Docker images Odoo và PostgreSQL.
- Khởi chạy container và ghi dữ liệu vào named volumes local.

Không được mở rộng ngoại lệ sang production environment, custom code, ingestion hoặc các file ngoài phạm vi đã phê duyệt.

## Kế hoạch thực hiện

1. Xác nhận Docker Engine và Docker Compose có sẵn bằng lệnh chỉ đọc.
2. Xác nhận port local dự kiến chưa bị chiếm dụng.
3. Xác nhận Odoo image tag và PostgreSQL version từ nguồn chính thức.
4. Tạo cấu trúc `odoo-erp/` và tài liệu hướng dẫn.
5. Tạo Compose configuration và `.env.example` trong phạm vi được phê duyệt.
6. Kiểm tra cấu hình bằng `docker compose config` mà không để lộ secret.
7. Pull image và khởi động stack sau khi có quyền rõ ràng.
8. Theo dõi health/status và log khởi động.
9. Mở giao diện Odoo local và tạo một database thử nghiệm thủ công.
10. Restart stack để xác nhận database và filestore được giữ lại.
11. Dừng stack mà không xóa volume.
12. Cập nhật kết quả kiểm tra và hạn chế trong task report.

## Tiêu chí nghiệm thu

- [ ] Odoo ERP simulator nằm đúng tại `services/data-source-simulators/odoo-erp/`.
- [ ] Compose configuration sử dụng Odoo 19 và PostgreSQL tương thích đã được pin version.
- [ ] `docker compose config` hợp lệ.
- [ ] Odoo và PostgreSQL khởi động thành công, không restart loop.
- [ ] Giao diện Odoo truy cập được qua URL local được ghi trong README.
- [ ] Có thể tạo và đăng nhập vào database Odoo thử nghiệm.
- [ ] Database và filestore vẫn tồn tại sau một lần restart stack.
- [ ] PostgreSQL không bị publish ra host nếu không có yêu cầu được phê duyệt.
- [ ] Không có secret thật, production data hoặc credential bị commit.
- [ ] Không có custom addon, custom module hoặc business logic được thêm.
- [ ] README có lệnh setup, start, status, logs, stop và reset an toàn.
- [ ] Cách reset có cảnh báo rõ thao tác xóa volume là destructive.
- [ ] README cấp simulator và cấp repository phản ánh đúng cấu trúc mới.

## Kiểm thử dự kiến

- [ ] Static validation: chạy `docker compose config`.
- [ ] Container status: xác nhận Odoo và PostgreSQL ở trạng thái running/healthy phù hợp.
- [ ] HTTP smoke test: xác nhận Odoo phản hồi trên cổng local.
- [ ] Manual UI test: tạo database thử nghiệm và đăng nhập.
- [ ] Persistence test: restart stack và xác nhận database vẫn tồn tại.
- [ ] Log review: không có lỗi kết nối hoặc xác thực PostgreSQL lặp lại.
- [ ] Security check: xác nhận không có secret thật và PostgreSQL không public ngoài ý muốn.
- [ ] Unit tests — Không áp dụng vì task chưa có custom executable code.
- [ ] Integration với ingestion — Không áp dụng trong task này.

## Kết quả

Chưa thực hiện. Kết quả, command đã chạy và bằng chứng kiểm tra sẽ được cập nhật sau khi task được triển khai.

## Rủi ro và phương án rollback

- Rủi ro: port Odoo mặc định có thể xung đột với service đang chạy trên máy local.
- Rủi ro: image mutable tag có thể thay đổi patch build; có thể pin digest sau khi xác nhận yêu cầu reproducibility.
- Rủi ro: credential mẫu yếu bị sử dụng nhầm ngoài local environment.
- Rủi ro: xóa named volume sẽ làm mất database và filestore local.
- Rollback an toàn: dừng stack bằng Docker Compose nhưng giữ named volumes.
- Rollback hoàn toàn: chỉ xóa container, network và named volumes sau khi chủ dự án xác nhận dữ liệu local không còn cần thiết.
- Hoàn tác codebase: chủ dự án review và xóa các file cấu hình/tài liệu đã thêm nếu không tiếp tục sử dụng Odoo simulator.

## Hạn chế và công việc tiếp theo

- Thiết kế và phê duyệt Odoo data domains cần sử dụng cho FMCG.
- Tạo task riêng để seed product, customer, outlet, warehouse và inventory data.
- Tạo task riêng cho Odoo API hoặc database/CDC data contract.
- Tạo task riêng cho ingestion connector từ Odoo vào raw layer.
- Tạo task riêng cho continuous business-event generation.
- Chỉ tạo custom addon sau khi có yêu cầu nghiệp vụ và phê duyệt phạm vi rõ ràng.

## Tài liệu tham khảo

- Odoo 19 On-premise documentation: https://www.odoo.com/documentation/19.0/administration/on_premise.html
- Odoo 19 source installation requirements: https://www.odoo.com/documentation/19.0/administration/on_premise/source.html
- Odoo Docker Official Image: https://hub.docker.com/_/odoo
