"""Create three operations for each simulator BoM. Run with Odoo shell."""
Model = env["mrp.routing.workcenter"]
centers = {r.code: r for r in env["mrp.workcenter"].search([("code", "in", ["MIX", "PROC", "FILL", "PACK"])])}
if len(centers) != 4:
    raise RuntimeError("Run 06_seed_mrp_workcenter.py first")
records = []
for bom in env["mrp.bom"].search([("product_tmpl_id.default_code", "!=", False)]):
    for sequence, name, code, minutes in [(10, "Mixing / Preparation", "MIX", 30), (20, "Processing", "PROC", 45), (30, "Filling and Packing", "PACK", 30)]:
        record = Model.search([("bom_id", "=", bom.id), ("sequence", "=", sequence)], limit=1)
        values = {"name": name, "bom_id": bom.id, "workcenter_id": centers[code].id, "sequence": sequence, "time_mode": "manual", "time_cycle": minutes}
        record.write(values) if record else None
        records.append(record or Model.create(values))
env.cr.commit()
print({"model": "mrp.routing.workcenter", "records": len(records)})
