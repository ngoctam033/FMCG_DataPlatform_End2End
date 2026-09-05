"""Create FMCG vendors and channel customers. Run with Odoo shell."""
Model = env["res.partner"].with_context(active_test=False)
vn = env.ref("base.vn")
terms = {r.name: r for r in env["account.payment.term"].search([])}
channels = {
    "GT": ("General Trade", "15 Days"), "MT": ("Modern Trade", "45 Days"),
    "DIST": ("Distributor", "30 Days"), "HORECA": ("HORECA", "21 Days"),
    "ECOM": ("E-commerce", "Immediate Payment"),
}
cities = ["Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Cần Thơ", "Hải Phòng"]
records = []
for channel, (pricelist_name, term_name) in channels.items():
    pricelist = env["product.pricelist"].search([("name", "=", pricelist_name)], limit=1)
    if not pricelist:
        raise RuntimeError("Run pricelist scripts before partner script")
    for index in range(1, 5):
        ref = "%s-CUST-%03d" % (channel, index)
        record = Model.search([("ref", "=", ref)], limit=1)
        values = {
            "name": "%s Customer %02d" % (pricelist_name, index), "ref": ref,
            "company_type": "company", "customer_rank": 1, "supplier_rank": 0,
            "street": "%d Đường Mô Phỏng" % index, "city": cities[index - 1],
            "country_id": vn.id, "phone": "+84 900 %03d %03d" % (list(channels).index(channel) + 1, index),
            "email": ref.lower() + "@example.test",
            "property_payment_term_id": terms[term_name].id,
            "property_product_pricelist": pricelist.id,
        }
        record.write(values) if record else None
        records.append(record or Model.create(values))
for vendor in Model.search([("supplier_rank", ">", 0)]):
    vendor.write({"country_id": vn.id, "property_supplier_payment_term_id": terms["30 Days"].id})
env.cr.commit()
print({"model": "res.partner", "customers": len(records), "vendors_updated": Model.search_count([("supplier_rank", ">", 0)])})
