# Rà soát các thay đổi đang được staged

Ngày rà soát: 2026-09-02  
Phạm vi: nội dung trả về bởi `git diff --cached` tại thời điểm kiểm tra

## Kết luận

Các thay đổi staged đã tạo được bộ khung chạy Odoo 19 cùng PostgreSQL và đưa bảy addon giao diện MuK vào repository. Cấu hình Compose, YAML, Python và XML đều vượt qua kiểm tra cú pháp cơ bản.

Tuy vậy, stack chưa nên được xem là sẵn sàng vận hành. PostgreSQL và Odoo filestore chưa có persistent volume; đồng thời chưa có quy trình khởi tạo database Odoo từ trạng thái sạch. Đây là hai vấn đề cần xử lý trước khi sử dụng stack để tạo dữ liệu cần được giữ lại.

Khuyến nghị: **chưa merge dưới trạng thái “ready to run”**. Có thể commit như một bản nháp nếu commit message và tài liệu nói rõ các hạn chế chưa được giải quyết.

## Nội dung đang staged

Staging area có:

- 304 file thay đổi.
- 12.714 dòng được thêm.
- 1 dòng bị xóa.
- 301 file nằm dưới `services/`.
- Khoảng 16 MiB addon Odoo.
- 78 file PNG.
- 63 file Python.
- 40 file JavaScript.
- 23 file XML.

Những thành phần chính:

- Root Compose tại `docker-compose.yaml`.
- Odoo 19 và PostgreSQL 15 tại `services/data-source-simulators/odoo-erp/deployment/docker-compose.odoo.yaml`.
- Cấu hình Odoo tại `services/data-source-simulators/odoo-erp/config/odoo.conf`.
- Các biến môi trường mẫu trong `.env.example`.
- Bảy addon: AppsBar, Chatter, Colors, Dialog, Groups, Web Refresh và Backend Theme.

## Các vấn đề cần xử lý

### 1. Database và filestore không được lưu bền vững

Mức độ: **Critical**

Service PostgreSQL đặt `PGDATA` tại `/var/lib/postgresql/data/pgdata`, nhưng không mount volume vào `/var/lib/postgresql/data`. Service Odoo cũng không mount volume vào `/var/lib/odoo`, dù đây là `data_dir` đã cấu hình.

Khi container bị remove và tạo lại:

- Database PostgreSQL có thể bị mất.
- Odoo filestore có thể bị mất.
- Metadata attachment trong database có thể không còn đồng bộ với file vật lý.

Cần bổ sung hai persistent volume độc lập và kiểm tra dữ liệu vẫn tồn tại sau một chu kỳ recreate container.

### 2. Chưa có quy trình khởi tạo database Odoo

Mức độ: **High**

PostgreSQL tạo database rỗng tên `fmcg_erp`. Odoo đồng thời được cấu hình:

```ini
db_name = fmcg_erp
dbfilter = ^fmcg_erp$
list_db = False
```

Stack không có init job, không chạy Odoo với bước cài `base`, và không mô tả thao tác tạo schema ban đầu. Vì `list_db` bị tắt, giao diện quản lý database cũng không phải một đường bootstrap rõ ràng.

Cần chọn một phương án khởi tạo có thể lặp lại và kiểm thử nó từ volume hoàn toàn mới.

### 3. Một số biến môi trường chưa được sử dụng

Mức độ: **Medium**

`.env.example` khai báo:

- `ODOO_ADMIN_LOGIN`
- `ODOO_ADMIN_PASSWORD`
- `ODOO_DB_LANGUAGE`
- `ODOO_DB_COUNTRY`

Không có Compose service hoặc script staged nào đọc các biến này. Người sử dụng có thể hiểu nhầm rằng tài khoản quản trị, ngôn ngữ và quốc gia sẽ được cấu hình tự động.

Nên xóa các biến chưa dùng hoặc triển khai rõ luồng bootstrap tiêu thụ chúng.

### 4. Addon mới chỉ được kiểm tra tĩnh

Mức độ: **High**

Bảy addon tác động đến web client, asset bundle, chatter, navbar, dialog, settings và action server. Việc Python compile và XML parse thành công chưa chứng minh rằng:

- Manifest và dependency load được trong Odoo 19.
- XPath khớp với view gốc.
- JavaScript/Owl module load thành công.
- SCSS và web assets build được.
- Các addon cài đặt, nâng cấp và gỡ bỏ an toàn.

Cần cài các addon vào database disposable, chạy test đi kèm và smoke-test các màn hình bị ảnh hưởng.

### 5. Chưa ghi lại nguồn gốc addon vendored

Mức độ: **Medium**

Các addon có manifest và license LGPL-3, nhưng repository chưa ghi rõ:

- Upstream repository hoặc nguồn tải.
- Commit, tag hoặc release gốc.
- Ngày lấy source.
- Checksum của gói nguồn.
- Quy trình cập nhật và so sánh với upstream.

Nên bổ sung inventory dependency bên thứ ba để bản build có thể tái tạo và dễ kiểm tra supply chain.

### 6. Healthcheck chưa phải readiness check đầy đủ

Mức độ: **Medium**

Healthcheck gọi:

```text
/web/health?db_server_status=true
```

Endpoint này có thể xác nhận tiến trình HTTP và trạng thái DB server, nhưng chưa chứng minh `fmcg_erp` đã được initialize, các addon đã cài hoặc asset đã build thành công.

Nên giữ healthcheck nhẹ cho container và bổ sung một smoke/readiness test riêng sau bước bootstrap.

### 7. Nhiễu whitespace và binary asset

Mức độ: **Low**

`git diff --cached --check` ghi nhận:

- 210 dòng có trailing whitespace.
- 105 trường hợp space-before-tab.
- 7 cảnh báo conflict marker giả do RST dùng dòng `=======` làm heading underline.

Không tìm thấy marker mở hoặc đóng conflict thật (`<<<<<<<` hoặc `>>>>>>>`).

Addon chứa 78 file PNG; file lớn nhất khoảng 2,1 MiB. Nhiều file là screenshot hoặc hình quảng bá. Nếu mục tiêu là giữ nguyên snapshot upstream thì có thể chấp nhận; nếu ưu tiên repository gọn, cần xác định asset nào không được runtime hoặc tài liệu sử dụng trước khi loại bỏ.

## Các kiểm tra đã thực hiện

| Kiểm tra | Kết quả |
|---|---|
| Render Docker Compose với password kiểm thử | Đạt |
| Parse hai file YAML | Đạt |
| Compile 63 file Python | Đạt |
| Parse 23 file XML | Đạt |
| Kiểm tra conflict marker thực | Không phát hiện |
| Dò credential bằng pattern cơ bản | Không phát hiện credential thật |
| Cài addon trên Odoo | Chưa thực hiện |
| Test JavaScript/Owl | Chưa thực hiện |
| Kiểm tra persistence | Chưa thực hiện |
| Kiểm tra bootstrap từ trạng thái sạch | Chưa thực hiện |

Phép dò credential chỉ là kiểm tra sơ bộ, không thay thế một secret scanner chuyên dụng.

## Thứ tự xử lý đề xuất

1. Thêm persistent volume cho PostgreSQL và `/var/lib/odoo`.
2. Thiết kế luồng bootstrap database có thể chạy lại an toàn.
3. Đồng bộ `.env.example` với các biến runtime thực sự sử dụng.
4. Ghi nguồn gốc và phiên bản chính xác của addon.
5. Cài addon trên database disposable và chạy test đi kèm.
6. Smoke-test giao diện, asset, chatter, dialog, navbar và refresh.
7. Quyết định giữ nguyên hay làm sạch whitespace và binary asset của upstream.

## Phạm vi chưa được đánh giá

Báo cáo không xác nhận chất lượng nghiệp vụ của addon, độ tương thích trình duyệt, hiệu năng, bảo mật ở cấp ứng dụng hoặc khả năng nâng cấp dữ liệu. Các nội dung đó cần môi trường Odoo đã bootstrap và một vòng kiểm thử riêng.

Trong quá trình rà soát và viết lại báo cáo, không có production code, addon hay runtime configuration nào được sửa.
