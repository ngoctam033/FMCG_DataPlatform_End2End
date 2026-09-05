"""Create one global discount rule per channel pricelist. Run with Odoo shell."""
Model = env["product.pricelist.item"]
discounts = {"General Trade": 3.0, "Modern Trade": 7.0, "Distributor": 12.0, "HORECA": 5.0, "E-commerce": 0.0}
records = []
for name, discount in discounts.items():
    pricelist = env["product.pricelist"].search([("name", "=", name)], limit=1)
    if not pricelist:
        raise RuntimeError("Run 03_seed_product_pricelist.py first: " + name)
    record = Model.search([("pricelist_id", "=", pricelist.id), ("applied_on", "=", "3_global"), ("min_quantity", "=", 0)], limit=1)
    values = {"pricelist_id": pricelist.id, "applied_on": "3_global", "compute_price": "percentage", "percent_price": discount, "min_quantity": 0}
    record.write(values) if record else None
    records.append(record or Model.create(values))
env.cr.commit()
print({"model": "product.pricelist.item", "records": len(records)})
