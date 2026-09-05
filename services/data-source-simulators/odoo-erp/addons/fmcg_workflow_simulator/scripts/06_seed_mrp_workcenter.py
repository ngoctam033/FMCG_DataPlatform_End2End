"""Create manufacturing work centers. Run with Odoo shell."""
Model = env["mrp.workcenter"].with_context(active_test=False)
calendar = env["resource.calendar"].search([("name", "=", "Standard 40 hours/week")], limit=1)
specs = [("Mixing", "MIX", 95, 450000), ("Processing / Sterilization", "PROC", 90, 650000), ("Filling", "FILL", 92, 550000), ("Packing", "PACK", 95, 350000), ("Cleaning", "CLEAN", 90, 250000)]
records = []
for name, code, efficiency, cost in specs:
    record = Model.search([("code", "=", code)], limit=1)
    values = {"name": name, "code": code, "time_efficiency": efficiency, "costs_hour": cost, "resource_calendar_id": calendar.id}
    record.write(values) if record else None
    records.append(record or Model.create(values))
env.cr.commit()
print({"model": "mrp.workcenter", "records": [(r.id, r.code) for r in records]})
