# External inventory simulator

Service này mô phỏng một hệ thống inventory bên ngoài. Container Python độc lập chỉ
kết nối đến Odoo qua JSON-2 HTTP API; không truy cập PostgreSQL, ORM, addons hoặc
filestore của Odoo.

Theo lịch mặc định mỗi 5 phút, service đọc dữ liệu nguồn qua API rồi tạo tối đa
`SIMULATOR_BATCH_SIZE` `stock.picking`. Mỗi picking được gửi bằng một API request
riêng, nên record đã tạo thành công không bị rollback theo record lỗi sau đó.

## Chuẩn bị và chạy

Tạo API key có quyền RPC cho user dùng để tạo dữ liệu, ưu tiên Inventory User
Simulator hoặc một user có quyền đọc master data và tạo `stock.picking`/`stock.move`.

Từ thư mục `deployment`:

```bash
export ODOO_API_KEY='replace-with-api-key'
docker compose -f docker-compose.odoo.yaml --profile simulator up -d --build inventory-simulator
docker compose -f docker-compose.odoo.yaml logs -f inventory-simulator
```

API key là secret, không commit vào repository.

| Biến | Mặc định | Ý nghĩa |
|---|---:|---|
| `ODOO_BASE_URL` | `http://odoo:8069` | URL Odoo từ container |
| `ODOO_DATABASE` | `fmcg_erp` | Database trong header `X-Odoo-Database` |
| `ODOO_API_KEY` | bắt buộc | Bearer API key |
| `SIMULATOR_CRON` | `*/5 * * * *` | Lịch chạy |
| `SIMULATOR_BATCH_SIZE` | `50` | Số picking mỗi đợt |
| `SIMULATOR_RUN_ON_START` | `true` | Chạy ngay khi service khởi động |
| `SIMULATOR_TIMEZONE` | `Asia/Ho_Chi_Minh` | Múi giờ của scheduler |
| `ODOO_REQUEST_TIMEOUT` | `120` | Timeout HTTP, đơn vị giây |
| `SIMULATOR_LOOKUP_PAGE_SIZE` | `500` | Kích thước trang khi đọc master data |
| `LOG_LEVEL` | `INFO` | Mức log |

## Logic dữ liệu

Mỗi lượt chạy, service đọc các model sau qua API:

- `res.partner`
- `stock.picking.type`
- `stock.location`
- `sale.order`
- `res.users`
- `product.product`
- `uom.uom`

Các field bắt buộc như `picking_type_id`, `location_id`, `location_dest_id`,
`product_id`, `product_uom` luôn được chọn từ record thật. Các field tùy chọn như
`partner_id`, `sale`, `user_id`, `location_final_id`, `packaging_uom_id` vẫn có
thể là `False`.

Nếu chọn được `sale.order`, service lấy `sale.order.line` hợp lệ để tạo `move_ids`.
Nếu không chọn sale, service random 1-3 sản phẩm.

## Kiểm tra và rollback

Các kiểm tra dưới đây không ghi dữ liệu:

```bash
python3 -m py_compile inventory-simulator/run.py
docker compose -f docker-compose.odoo.yaml --profile simulator config --quiet
```

Để rollback code, bỏ service và thư mục simulator. Các picking đã tạo cần được
hủy hoặc xóa thủ công trong Odoo theo quy trình của môi trường thử nghiệm.
