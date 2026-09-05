"""Create and update logistics package types. Run with Odoo shell."""

Model = env["stock.package.type"]

specs = [
    ("Thùng carton FMCG", "disposable", 10, 30, 40, 50, .5, 15),
    ("Màng co lốc chai", "disposable", 20, 12, 14, 24, .05, 3),
    ("Euro Pallet", "reusable", 30, 15, 80, 120, 25, 1000),
    ("Picking Tote", "reusable", 40, 32, 40, 60, 2, 25),
    ("Thùng giữ nhiệt", "reusable", 50, 45, 50, 60, 5, 40),
]

records = []

for name, use, sequence, height, width, length, base, maximum in specs:
    record = Model.search(
        [
            ("name", "=", name),
            ("company_id", "=", env.company.id),
        ],
        limit=11,
    )

    values = {
        "name": name,
        "package_use": use,
        "sequence": sequence,
        "height": height,
        "width": width,
        "packaging_length": length,
        "base_weight": base,
        "max_weight": maximum,
    }

    if record:
        # Không truyền company_id vào write(), tránh kích hoạt lỗi tạo
        # ir.sequence thiếu name trong Odoo 19.
        record.write(values)
    else:
        record = Model.create({
            **values,
            "company_id": env.company.id,
        })

    records.append(record)

env.cr.commit()

print({
    "model": "stock.package.type",
    "records": [(record.id, record.name) for record in records],
})