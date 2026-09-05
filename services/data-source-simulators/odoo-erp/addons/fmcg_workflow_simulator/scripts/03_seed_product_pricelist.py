"""Create channel pricelists. Run with Odoo shell."""
Model = env["product.pricelist"].with_context(active_test=False)
currency = env.ref("base.VND")
names = ["General Trade", "Modern Trade", "Distributor", "HORECA", "E-commerce"]
records = []
for name in names:
    record = Model.search([("name", "=", name)], limit=1)
    values = {"name": name, "currency_id": currency.id, "company_id": env.company.id, "active": True}
    record.write(values) if record else None
    records.append(record or Model.create(values))
env.cr.commit()
print({"model": "product.pricelist", "records": [(r.id, r.name) for r in records]})
