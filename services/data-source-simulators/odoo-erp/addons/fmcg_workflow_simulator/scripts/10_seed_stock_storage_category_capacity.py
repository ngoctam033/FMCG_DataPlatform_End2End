"""Create pallet/tote capacities for storage categories. Run with Odoo shell."""
Model = env["stock.storage.category.capacity"]
categories = env["stock.storage.category"].search([])
packages = env["stock.package.type"].search([("name", "in", ["Euro Pallet", "Picking Tote", "Thùng giữ nhiệt"])])
if not categories or not packages:
    raise RuntimeError("Run package type and storage category scripts first")
records = []
for category in categories.filtered(lambda c: c.name in ["Food Grade Storage", "Finished Goods", "Packaging Storage", "Chemical Storage", "Cold Storage", "Frozen Storage"]):
    for package in packages:
        quantity = 20 if package.name == "Euro Pallet" else 100
        record = Model.search([("storage_category_id", "=", category.id), ("package_type_id", "=", package.id)], limit=1)
        values = {"storage_category_id": category.id, "package_type_id": package.id, "quantity": quantity}
        record.write(values) if record else None
        records.append(record or Model.create(values))
env.cr.commit()
print({"model": "stock.storage.category.capacity", "records": len(records)})
