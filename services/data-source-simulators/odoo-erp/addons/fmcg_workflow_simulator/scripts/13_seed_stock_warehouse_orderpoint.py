"""Create min/max replenishment policies. Run with Odoo shell."""
Model = env["stock.warehouse.orderpoint"]
warehouse = env["stock.warehouse"].search([], limit=1)
products = env["product.product"].search([("is_storable", "=", True), ("purchase_ok", "=", True), ("default_code", "!=", False)])
records = []
for product in products:
    unit_name = product.uom_id.name
    minimum, maximum = ((500, 2500) if unit_name in ["kg", "L"] else (100, 500))
    record = Model.search([("product_id", "=", product.id), ("location_id", "=", warehouse.lot_stock_id.id)], limit=1)
    values = {"product_id": product.id, "location_id": warehouse.lot_stock_id.id, "product_min_qty": minimum, "product_max_qty": maximum, "trigger": "auto"}
    record.write(values) if record else None
    records.append(record or Model.create(values))
env.cr.commit()
print({"model": "stock.warehouse.orderpoint", "records": len(records)})
