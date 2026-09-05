"""Seed idempotent supplier and customer master data via ``odoo shell``.

The data is synthetic. Email addresses use the reserved ``example.test`` domain,
and VAT identifiers are intentionally omitted.
"""

Partner = env["res.partner"].with_context(active_test=False)
SupplierInfo = env["product.supplierinfo"]
Tag = env["res.partner.category"]
Term = env["account.payment.term"]
Country = env["res.country"]
State = env["res.country.state"]

vietnam = Country.search([("code", "=", "VN")], limit=1)
if not vietnam:
    raise RuntimeError("Vietnam country master data is required")


def get_term(name):
    term = Term.search([("name", "=", name)], limit=1)
    if not term:
        raise RuntimeError(f"Missing payment term: {name}")
    return term


terms = {name: get_term(name) for name in ("Immediate Payment", "15 Days", "30 Days", "45 Days")}


def get_tag(name):
    return Tag.search([("name", "=", name)], limit=1) or Tag.create({"name": name})


tags = {name: get_tag(name) for name in (
    "FMCG / Supplier", "FMCG / General Trade", "FMCG / Modern Trade",
    "FMCG / HORECA", "FMCG / E-commerce", "FMCG / Distributor",
)}


def state(code):
    return State.search([("country_id", "=", vietnam.id), ("code", "=", code)], limit=1)


created = []
updated = []


def upsert(ref, values):
    record = Partner.search([("ref", "=", ref)], limit=1)
    values = dict(values, ref=ref, active=True, country_id=vietnam.id)
    if record:
        record.write(values)
        updated.append(ref)
    else:
        record = Partner.create(values)
        created.append(ref)
    return record


supplier_specs = [
    ("SUP-DAIRY", "Nhà cung cấp Sữa nguyên liệu Miền Nam", "VN-79", "Khu công nghiệp Tân Tạo", "TP. Hồ Chí Minh", "02873001001", "dairy.supplier@example.test", "15 Days"),
    ("SUP-INGREDIENTS", "Nhà cung cấp Đường & Gia vị Việt", "VN-57", "Khu công nghiệp Sóng Thần", "Bình Dương", "02747300102", "ingredients.supplier@example.test", "30 Days"),
    ("SUP-PACKAGING", "Bao bì FMCG Đông Nam", "VN-39", "Khu công nghiệp Amata", "Đồng Nai", "02517300103", "packaging.supplier@example.test", "30 Days"),
    ("SUP-CHEMICAL", "Nguyên liệu Hóa phẩm An Phát", "VN-79", "Khu công nghiệp Hiệp Phước", "TP. Hồ Chí Minh", "02873001004", "chemical.supplier@example.test", "30 Days"),
    ("SUP-TRADING", "Nhà phân phối Hàng tiêu dùng Toàn Việt", "VN-01", "Khu công nghiệp Bắc Thăng Long", "Hà Nội", "02473001005", "trading.supplier@example.test", "45 Days"),
    ("SUP-FROZEN", "Thực phẩm Đông lạnh Biển Xanh", "VN-48", "Khu công nghiệp Vĩnh Lộc", "TP. Hồ Chí Minh", "02873001006", "frozen.supplier@example.test", "15 Days"),
    ("SUP-LOGISTICS", "Vận tải & Kho lạnh Nam Việt", "VN-79", "Đường Nguyễn Văn Linh", "TP. Hồ Chí Minh", "02873001007", "logistics.supplier@example.test", "15 Days"),
    ("SUP-GENERAL", "Nhà cung cấp FMCG tổng hợp (Simulator)", "VN-79", "Đường Võ Văn Kiệt", "TP. Hồ Chí Minh", "02873001008", "general.supplier@example.test", "30 Days"),
]

suppliers = []
for ref, name, state_code, street, city, phone, email, term_name in supplier_specs:
    suppliers.append(upsert(ref, {
        "name": name, "company_type": "company", "supplier_rank": 1,
        "customer_rank": 0, "street": street, "city": city,
        "state_id": state(state_code).id or False, "phone": phone, "email": email,
        "property_supplier_payment_term_id": terms[term_name].id,
        "category_id": [(6, 0, tags["FMCG / Supplier"].ids)],
    }))

# Script 01 originally created this supplier without a stable reference. Adopt
# its product price lists and archive the legacy duplicate without deleting it.
general_supplier = Partner.search([("ref", "=", "SUP-GENERAL")], limit=1)
legacy_general_suppliers = Partner.search([
    ("id", "!=", general_supplier.id),
    ("ref", "=", False),
    ("name", "=", "Nhà cung cấp FMCG tổng hợp (Simulator)"),
])
if legacy_general_suppliers:
    SupplierInfo.search([("partner_id", "in", legacy_general_suppliers.ids)]).write({
        "partner_id": general_supplier.id,
    })
    legacy_general_suppliers.write({"active": False})


customer_specs = [
    # ref, name, channel, province code, city, payment term, credit limit
    ("CUS-GT-001", "Tạp hóa Minh Anh", "General Trade", "VN-79", "TP. Hồ Chí Minh", "15 Days", 30_000_000),
    ("CUS-GT-002", "Cửa hàng Bách hóa Thành Công", "General Trade", "VN-39", "Biên Hòa", "15 Days", 40_000_000),
    ("CUS-GT-003", "Đại lý Tiêu dùng Hồng Phúc", "General Trade", "VN-57", "Thủ Dầu Một", "30 Days", 80_000_000),
    ("CUS-GT-004", "Tạp hóa Gia Đình", "General Trade", "VN-41", "Long Xuyên", "15 Days", 25_000_000),
    ("CUS-GT-005", "Đại lý Phương Nam", "General Trade", "VN-92", "Cần Thơ", "30 Days", 70_000_000),
    ("CUS-GT-006", "Cửa hàng Tiện lợi Bình Minh", "General Trade", "VN-48", "TP. Hồ Chí Minh", "15 Days", 35_000_000),
    ("CUS-MT-001", "Siêu thị Thành Thị Miền Nam", "Modern Trade", "VN-79", "TP. Hồ Chí Minh", "45 Days", 1_500_000_000),
    ("CUS-MT-002", "Chuỗi Minimart Sao Việt", "Modern Trade", "VN-57", "Bình Dương", "45 Days", 900_000_000),
    ("CUS-MT-003", "Trung tâm Bán lẻ Đồng Nai", "Modern Trade", "VN-39", "Đồng Nai", "45 Days", 700_000_000),
    ("CUS-MT-004", "Siêu thị Miền Tây", "Modern Trade", "VN-92", "Cần Thơ", "45 Days", 800_000_000),
    ("CUS-HR-001", "Khách sạn Sông Sài Gòn", "HORECA", "VN-79", "TP. Hồ Chí Minh", "30 Days", 250_000_000),
    ("CUS-HR-002", "Chuỗi Café Ban Mai", "HORECA", "VN-79", "TP. Hồ Chí Minh", "30 Days", 180_000_000),
    ("CUS-HR-003", "Nhà hàng Hương Việt", "HORECA", "VN-48", "TP. Hồ Chí Minh", "15 Days", 100_000_000),
    ("CUS-HR-004", "Công ty Suất ăn Công nghiệp An Khang", "HORECA", "VN-57", "Bình Dương", "30 Days", 350_000_000),
    ("CUS-EC-001", "Khách hàng Online Hồ Chí Minh", "E-commerce", "VN-79", "TP. Hồ Chí Minh", "Immediate Payment", 0),
    ("CUS-EC-002", "Khách hàng Online Đồng Nai", "E-commerce", "VN-39", "Đồng Nai", "Immediate Payment", 0),
    ("CUS-EC-003", "Khách hàng Online Cần Thơ", "E-commerce", "VN-92", "Cần Thơ", "Immediate Payment", 0),
    ("CUS-DIS-001", "Nhà phân phối Miền Đông", "Distributor", "VN-39", "Đồng Nai", "30 Days", 2_000_000_000),
    ("CUS-DIS-002", "Nhà phân phối Tây Nam Bộ", "Distributor", "VN-92", "Cần Thơ", "30 Days", 2_500_000_000),
    ("CUS-DIS-003", "Nhà phân phối Cao Nguyên", "Distributor", "VN-35", "Lâm Đồng", "30 Days", 1_800_000_000),
]

channel_tags = {
    "General Trade": tags["FMCG / General Trade"],
    "Modern Trade": tags["FMCG / Modern Trade"],
    "HORECA": tags["FMCG / HORECA"],
    "E-commerce": tags["FMCG / E-commerce"],
    "Distributor": tags["FMCG / Distributor"],
}

customers = []
delivery_addresses = []
for index, (ref, name, channel, state_code, city, term_name, credit_limit) in enumerate(customer_specs, 1):
    customer = upsert(ref, {
        "name": name, "company_type": "company", "customer_rank": 1,
        "supplier_rank": 0, "street": f"Địa chỉ mô phỏng {index}, {city}",
        "city": city, "state_id": state(state_code).id or False,
        "phone": f"0901{index:06d}", "email": f"customer{index:02d}@example.test",
        "property_payment_term_id": terms[term_name].id,
        "credit_limit": credit_limit,
        "category_id": [(6, 0, channel_tags[channel].ids)],
    })
    customers.append(customer)
    delivery_addresses.append(upsert(ref + "-SHIP", {
        "name": "Kho nhận hàng – " + name, "company_type": "person",
        "parent_id": customer.id, "type": "delivery",
        "street": f"Kho giao nhận mô phỏng {index}, {city}", "city": city,
        "state_id": state(state_code).id or False, "phone": f"0902{index:06d}",
        "customer_rank": 0, "supplier_rank": 0,
    }))

env.cr.commit()
print({
    "created": len(created), "updated": len(updated),
    "suppliers": len(suppliers), "customers": len(customers),
    "delivery_addresses": len(delivery_addresses), "tags": len(tags),
})
