"""Create warehouse storage categories. Run with Odoo shell."""
Model = env["stock.storage.category"]
specs = [("Food Grade Storage", 20000, "mixed"), ("Finished Goods", 25000, "mixed"), ("Packaging Storage", 15000, "mixed"), ("Chemical Storage", 12000, "same"), ("Cold Storage", 10000, "same"), ("Frozen Storage", 8000, "same")]
records = []
for name, weight, policy in specs:
    record = Model.search([("name", "=", name)], limit=1)
    values = {"name": name, "max_weight": weight, "allow_new_product": policy, "company_id": env.company.id}
    record.write(values) if record else None
    records.append(record or Model.create(values))
env.cr.commit()
print({"model": "stock.storage.category", "records": len(records)})
