"""Create storage zones below WH/Stock. Run with Odoo shell."""
Model = env["stock.location"].with_context(active_test=False)
warehouse = env["stock.warehouse"].search([], limit=1)
specs = [("Food Raw Materials", "Food Grade Storage"), ("Finished Food", "Finished Goods"), ("Packaging", "Packaging Storage"), ("Chemicals", "Chemical Storage"), ("Cold Chain", "Cold Storage"), ("Frozen", "Frozen Storage")]
records = []
for name, storage_name in specs:
    storage = env["stock.storage.category"].search([("name", "=", storage_name)], limit=1)
    if not storage:
        raise RuntimeError("Run 09_seed_stock_storage_category.py first")
    record = Model.search([("name", "=", name), ("location_id", "=", warehouse.lot_stock_id.id)], limit=1)
    values = {"name": name, "location_id": warehouse.lot_stock_id.id, "usage": "internal", "storage_category_id": storage.id, "company_id": env.company.id, "active": True}
    record.write(values) if record else None
    records.append(record or Model.create(values))
env.cr.commit()
print({"model": "stock.location", "records": [(r.id, r.complete_name) for r in records]})
