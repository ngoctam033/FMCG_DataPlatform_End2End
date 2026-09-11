# Phân Tích Logic Orderpoint và Action Replenish Trong Odoo

Tài liệu này lưu lại kết quả nghiên cứu về hàm `action_replenish` của đối tượng `stock.warehouse.orderpoint` và các trường hợp ngoại lệ khi gọi hàm này tự động từ Simulator Cron (`cron_inventory_replenish_new`).

## Bối cảnh

Trong phương thức `cron_inventory_replenish_new` của class `FmcgSimulatorRun` (file `models/simulator.py`), hệ thống quét các quy tắc tái cung ứng (orderpoints) dựa trên domain search:

```python
def _get_replenishment_orderpoints(self, categories):
    return self.env["stock.warehouse.orderpoint"].search([
        ("company_id", "=", self.env.company.id),
        ("product_id.active", "=", True),
        ("product_id.purchase_ok", "=", True),
        ("product_id.is_storable", "=", True),
        ("product_id.categ_id", "child_of", categories.ids),
    ], order="id")
```

Sau khi lấy danh sách `orderpoints`, hệ thống gọi hàm:
```python
orderpoints.action_replenish()
```

## Câu hỏi nghiên cứu
> *Có những case nào thỏa mãn kết quả tìm kiếm của hàm `_get_replenishment_orderpoints` nhưng lại **không được phép** hoặc **không sinh ra kết quả** khi gọi `action_replenish` không?*

## Kết quả phân tích (Các Edge Cases)

Dựa vào mã nguồn của Odoo (hàm `action_replenish` và `_procure_orderpoint_confirm` trong module `stock`), dưới đây là 4 trường hợp ngoại lệ quan trọng:

### 1. Tồn kho đã đủ (Lượng cần đặt `qty_to_order <= 0`)
Mặc dù bạn query ra toàn bộ orderpoint, nhưng khi hàm `action_replenish()` chạy, nó sẽ kiểm tra số lượng:
```python
# Trích xuất từ core Odoo: _procure_orderpoint_confirm()
if orderpoint.product_uom.compare(orderpoint.qty_to_order, 0.0) == 1: 
    # Chỉ chạy tạo PO/Picking khi qty_to_order > 0
```
- **Hệ quả:** Nếu tồn kho dự kiến của sản phẩm đã thỏa mãn mức an toàn (không bị rớt dưới `min_qty` đối với rule auto, hoặc đã đủ `max_qty`), `qty_to_order` tính ra sẽ `<= 0`. Odoo sẽ **bỏ qua hoàn toàn** việc chạy Procurement cho orderpoint đó.
- **Tác động:** Việc gọi đè `action_replenish` là vô hại (không báo lỗi), nhưng sẽ không có record nào mới (Purchase Order, Picking) được tạo ra.

### 2. Orderpoint đang bị người dùng "Snooze" (Tạm hoãn)
Trong giao diện Replenishment Dashboard của Odoo, người quản lý kho có quyền bấm **"Snooze"** một orderpoint (vd: tạm hoãn nhắc nhở mua hàng trong 7 ngày). Khi đó trường `snoozed_until` sẽ được thiết lập thành một mốc thời gian trong tương lai.
- **Hệ quả:** Hàm search hiện tại của Simulator đang **không kiểm tra** trường `snoozed_until`. 
- **Tác động:** Simulator sẽ lấy luôn cả những orderpoint mà user đang muốn tạm hoãn, và ép nó chạy `action_replenish()`. Điều này đi ngược lại với mong muốn tạm hoãn của người dùng.
- **Giải pháp:** Cần bổ sung filter vào domain:
  ```python
  "|", ("snoozed_until", "=", False), ("snoozed_until", "<=", fields.Date.today())
  ```

### 3. Sản phẩm bị thiếu cấu hình Route hoặc Nhà cung cấp (Vendor)
Domain search chỉ kiểm tra `purchase_ok = True`, nhưng không đảm bảo 100% về cấu hình chi tiết:
1. Sản phẩm đó đã được gắn nhà cung cấp (Vendor) hợp lệ chưa?
2. Tuyến đường (Route) trên orderpoint hoặc trên sản phẩm có hợp lệ không (vd: có route `Buy` hoặc `Manufacture` không)?
- **Hệ quả:** `action_replenish` vẫn sẽ được gọi, nhưng core Odoo sẽ văng ra Exception `ProcurementException` (lỗi không tìm thấy Vendor matching) ở backend. 
- **Tác động:** Hàm `_procure_orderpoint_confirm` sẽ bắt (catch) lỗi này nên không làm crash server Simulator. Tuy nhiên, nó sẽ **không tạo ra Purchase Order**, thay vào đó tự động sinh ra một Activity (Cảnh báo) trên form của Product Template để nhắc nhở User cấu hình lại.

### 4. Xung đột logic với Trigger tự động (`trigger = 'auto'`)
Orderpoint trong Odoo có 2 loại trigger là **Manual** (chờ người ấn Order) và **Auto** (Hệ thống tự quét).
- **Hệ quả:** Domain hiện tại lấy toàn bộ orderpoint bất kể trigger type. Những rule `auto` về nguyên tắc đã được xử lý bởi cron job ngầm của Odoo (`procurement.jit` hoặc scheduler).
- **Tác động:** Dù gọi `action_replenish` trên rule `auto` cũng không sinh lỗi (do Odoo sẽ tự cân đối lại `qty_to_order`), nhưng về mặt bản chất Simulator đang thực hiện trùng lặp một công việc mà hệ thống chuẩn đã làm. Nếu mục đích của Simulator là giả lập *người dùng click vào nút Order On Demand*, thì chỉ nên query các rule có `trigger = 'manual'`.
