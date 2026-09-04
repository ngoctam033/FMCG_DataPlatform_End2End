"""Idempotent FMCG product catalog seed for execution with ``odoo shell``.

Run inside the Odoo container; the shell injects the global ``env`` object.
The barcodes use an internal-use prefix and are not commercial GS1 assignments.
"""

Product = env["product.template"].with_context(active_test=False)
Category = env["product.category"]
Uom = env["uom.uom"]
Bom = env["mrp.bom"]
SupplierInfo = env["product.supplierinfo"]
Partner = env["res.partner"]

unit = env.ref("uom.product_uom_unit")
litre = env.ref("uom.product_uom_litre")
kg = env.ref("uom.product_uom_kgm")
fefo = env["product.removal"].search([("method", "=", "fefo")], limit=1)
mto = env["stock.route"].search([("name", "=", "Replenish on Order (MTO)")], limit=1)
food = Category.search([("name", "=", "Food"), ("parent_id", "=", False)], limit=1)
goods = Category.search([("name", "=", "Goods"), ("parent_id", "=", False)], limit=1)


def get_category(name, parent, use_fefo=False):
    record = Category.search([("name", "=", name), ("parent_id", "=", parent.id)], limit=1)
    record = record or Category.create({"name": name, "parent_id": parent.id})
    if use_fefo:
        record.removal_strategy_id = fefo
    return record


categories = {
    key: get_category(name, parent, expiring)
    for key, name, parent, expiring in [
        ("bev", "Nước giải khát", food, True),
        ("instant", "Thực phẩm ăn liền", food, True),
        ("snack", "Bánh kẹo & Snack", food, True),
        ("cond", "Gia vị", food, True),
        ("frozen", "Hàng đông lạnh", food, True),
        ("personal", "Chăm sóc cá nhân", goods, False),
        ("home", "Chăm sóc gia đình", goods, False),
        ("raw", "Nguyên liệu đa ngành", food, True),
        ("pack", "Bao bì đa ngành", goods, False),
        ("trade", "Hàng thương mại", goods, False),
    ]
}


def get_unit(name):
    record = Uom.search([("name", "=", name)], limit=1)
    record = record or Uom.create({
        "name": name, "relative_uom_id": unit.id,
        "relative_factor": 1.0, "rounding": 1.0,
    })
    record.rounding = 1.0
    return record


bottle = Uom.search([("name", "=", "Chai")], limit=1)
can, packet, bag, box = [get_unit(name) for name in ("Lon", "Gói", "Túi", "Hộp")]
vendor = Partner.search([("name", "=", "Nhà cung cấp FMCG tổng hợp (Simulator)")], limit=1)
vendor = vendor or Partner.create({
    "name": "Nhà cung cấp FMCG tổng hợp (Simulator)",
    "company_type": "company", "supplier_rank": 1,
    "email": "general.supplier@example.test",
})


def ean13(number):
    base = "200001" + str(number).zfill(6)
    checksum = -sum((3 if index % 2 else 1) * int(char) for index, char in enumerate(base)) % 10
    return base + str(checksum)


created = []
updated = []


def upsert_product(code, name, sequence, category, uom, cost, *, sale=False,
                   price=0.0, expiry=0, manufactured=False, weight=1.0, volume=0.0):
    product = Product.search([("default_code", "=", code)], limit=1)
    values = {
        "name": name, "default_code": code, "barcode": ean13(sequence),
        "categ_id": category.id, "uom_id": uom.id, "is_storable": True,
        "sale_ok": sale, "purchase_ok": not manufactured,
        "invoice_policy": "delivery", "tracking": "lot" if expiry else "none",
        "standard_price": cost, "list_price": price, "weight": weight,
        "volume": volume, "description_sale": name + " – dữ liệu mô phỏng FMCG.",
    }
    if expiry:
        values.update({
            "use_expiration_date": True, "expiration_time": expiry,
            "use_time": max(7, expiry // 12), "removal_time": max(14, expiry // 8),
            "alert_time": max(21, expiry // 6),
        })
    if manufactured:
        values.update({"purchase_ok": False, "route_ids": [(6, 0, mto.ids)]})
    if product:
        product.write(values)
        updated.append(code)
    else:
        product = Product.create(values)
        created.append(code)
    if not manufactured:
        seller = SupplierInfo.search([
            ("partner_id", "=", vendor.id), ("product_tmpl_id", "=", product.id)
        ], limit=1)
        seller_values = {
            "partner_id": vendor.id, "product_tmpl_id": product.id,
            "price": cost, "min_qty": 10, "delay": 7,
        }
        seller.write(seller_values) if seller else SupplierInfo.create(seller_values)
    return product


input_specs = {
    "w": ("RM-PURIFIED-WATER", "Nước tinh khiết sản xuất", 301, "raw", litre, 1200, 30),
    "f": ("RM-WHEAT-FLOUR", "Bột mì thực phẩm", 302, "raw", kg, 18000, 365),
    "s": ("RM-SEASONING", "Gia vị tổng hợp", 303, "raw", kg, 95000, 365),
    "p": ("RM-POTATO", "Khoai tây nguyên liệu", 304, "raw", kg, 16000, 30),
    "o": ("RM-VEG-OIL", "Dầu thực vật", 305, "raw", litre, 42000, 365),
    "c": ("RM-CLEANING-BASE", "Hỗn hợp nền tẩy rửa", 306, "raw", litre, 28000, 730),
    "h": ("RM-CHILI-PASTE", "Ớt nghiền nguyên liệu", 307, "raw", kg, 38000, 180),
    "b": ("PM-BOTTLE-GENERIC", "Chai nhựa thực phẩm", 308, "pack", unit, 1200, 0),
    "n": ("PM-CAN-330", "Lon nhôm 330ml", 309, "pack", unit, 1800, 0),
    "q": ("PM-POUCH-GENERIC", "Túi và gói bao bì", 310, "pack", unit, 700, 0),
}
inputs = {
    key: upsert_product(code, name, seq, categories[cat], uom, cost, expiry=expiry)
    for key, (code, name, seq, cat, uom, cost, expiry) in input_specs.items()
}


def upsert_manufactured(spec):
    code, name, seq, cat, uom, price, cost, expiry, components, weight, volume = spec
    product = upsert_product(
        code, name, seq, categories[cat], uom, cost, sale=True, price=price,
        expiry=expiry, manufactured=True, weight=weight, volume=volume,
    )
    lines = [(0, 0, {
        "product_id": inputs[key].product_variant_id.id,
        "product_qty": quantity, "product_uom_id": line_uom.id,
    }) for key, quantity, line_uom in components]
    bom = Bom.search([("product_tmpl_id", "=", product.id), ("type", "=", "normal")], limit=1)
    values = {
        "product_tmpl_id": product.id, "product_qty": 1.0,
        "product_uom_id": uom.id, "type": "normal",
        "bom_line_ids": [(5, 0, 0)] + lines,
    }
    bom.write(values) if bom else Bom.create(values)
    return product


manufactured_specs = [
    ("BEV-WATER-500", "Nước tinh khiết 500ml", 401, "bev", bottle, 6000, 2500, 365, [("w", .5, litre), ("b", 1, unit)], .52, .00065),
    ("BEV-TEA-PEACH-450", "Trà đào đóng chai 450ml", 402, "bev", bottle, 12000, 6000, 270, [("w", .43, litre), ("s", .01, kg), ("b", 1, unit)], .47, .0006),
    ("BEV-COLA-330", "Nước ngọt có gas 330ml", 403, "bev", can, 10000, 5000, 270, [("w", .31, litre), ("s", .015, kg), ("n", 1, unit)], .35, .00045),
    ("FOOD-NOODLE-BEEF-75", "Mì ăn liền vị bò 75g", 404, "instant", packet, 5000, 2600, 180, [("f", .06, kg), ("s", .01, kg), ("o", .005, litre), ("q", 1, unit)], .08, .0004),
    ("FOOD-SNACK-POTATO-50", "Snack khoai tây 50g", 405, "snack", packet, 10000, 4800, 180, [("p", .08, kg), ("o", .012, litre), ("s", .003, kg), ("q", 1, unit)], .055, .0008),
    ("COND-CHILI-250", "Tương ớt chai 250g", 406, "cond", bottle, 18000, 9000, 365, [("h", .2, kg), ("w", .04, litre), ("s", .01, kg), ("b", 1, unit)], .28, .0004),
    ("HOME-DISH-750", "Nước rửa chén 750ml", 407, "home", bottle, 35000, 17000, 730, [("c", .72, litre), ("w", .03, litre), ("b", 1, unit)], .8, .001),
    ("HOME-LAUNDRY-3L", "Nước giặt 3L", 408, "home", bottle, 145000, 72000, 730, [("c", 2.85, litre), ("w", .15, litre), ("b", 1, unit)], 3.1, .0035),
]
manufactured = [upsert_manufactured(spec) for spec in manufactured_specs]

trading_specs = [
    ("TRADE-TISSUE-10", "Khăn giấy lốc 10 gói", 501, "trade", packet, 42000, 65000, 0),
    ("TRADE-TOOTHPASTE-180", "Kem đánh răng 180g", 502, "personal", box, 33000, 52000, 1095),
    ("TRADE-SHAMPOO-650", "Dầu gội 650ml", 503, "personal", bottle, 85000, 135000, 1095),
    ("TRADE-SHOWER-GEL-500", "Sữa tắm 500ml", 504, "personal", bottle, 68000, 110000, 1095),
    ("TRADE-HANDWASH-500", "Nước rửa tay 500ml", 505, "personal", bottle, 45000, 75000, 730),
    ("TRADE-FLOOR-CLEANER-1L", "Nước lau sàn 1L", 506, "home", bottle, 35000, 58000, 730),
    ("TRADE-FABRIC-SOFTENER-2L", "Nước xả vải 2L", 507, "home", bag, 58000, 95000, 730),
    ("TRADE-COFFEE-3IN1-20", "Cà phê hòa tan hộp 20 gói", 508, "instant", box, 48000, 78000, 365),
    ("TRADE-BISCUIT-300", "Bánh quy bơ hộp 300g", 509, "snack", box, 39000, 65000, 270),
    ("TRADE-FISH-SAUCE-750", "Nước mắm 750ml", 510, "cond", bottle, 41000, 68000, 730),
    ("FROZEN-DUMPLING-500", "Há cảo đông lạnh 500g", 511, "frozen", bag, 55000, 89000, 365),
    ("FROZEN-ICECREAM-450", "Kem hộp 450ml", 512, "frozen", box, 60000, 95000, 365),
]
trading = [
    upsert_product(code, name, seq, categories[cat], uom, cost, sale=True,
                   price=price, expiry=expiry)
    for code, name, seq, cat, uom, cost, price, expiry in trading_specs
]

env.cr.commit()
print({
    "created": len(created), "updated": len(updated),
    "catalog_products": len(inputs) + len(manufactured) + len(trading),
    "manufactured": len(manufactured), "trading": len(trading),
    "inputs": len(inputs),
})
