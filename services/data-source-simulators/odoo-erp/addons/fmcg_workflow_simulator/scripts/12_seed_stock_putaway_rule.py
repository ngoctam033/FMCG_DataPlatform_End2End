"""Create category-based putaway rules for WH/Stock. Run with Odoo shell."""
Model = env["stock.putaway.rule"]
warehouse = env["stock.warehouse"].search([], limit=1)
mapping = {"Nguyên liệu đa ngành": "Food Raw Materials", "Nguyên liệu": "Food Raw Materials", "Sữa & sản phẩm từ sữa": "Finished Food", "Nước giải khát": "Finished Food", "Thực phẩm ăn liền": "Finished Food", "Bánh kẹo & Snack": "Finished Food", "Gia vị": "Finished Food", "Bao bì đa ngành": "Packaging", "Bao bì": "Packaging", "Chăm sóc gia đình": "Chemicals", "Hàng đông lạnh": "Frozen"}
records = []
for category_name, location_name in mapping.items():
    category = env["product.category"].search([("name", "=", category_name)], limit=1)
    location = env["stock.location"].search([("name", "=", location_name), ("location_id", "=", warehouse.lot_stock_id.id)], limit=1)
    if not category or not location:
        continue
    record = Model.search([("location_in_id", "=", warehouse.lot_stock_id.id), ("category_id", "=", category.id)], limit=1)
    values = {"location_in_id": warehouse.lot_stock_id.id, "location_out_id": location.id, "category_id": category.id, "product_id": False, "sequence": 10}
    record.write(values) if record else None
    records.append(record or Model.create(values))
env.cr.commit()
print({"model": "stock.putaway.rule", "records": len(records)})
