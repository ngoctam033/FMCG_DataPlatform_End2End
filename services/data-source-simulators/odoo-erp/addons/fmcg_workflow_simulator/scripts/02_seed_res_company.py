"""Configure the simulator company. Run with Odoo shell."""
company = env.company
company.write({
    "name": "Công ty FMCG Việt Nam",
    "country_id": env.ref("base.vn").id,
    "currency_id": env.ref("base.VND").id,
    "street": "01 Đường Nguyễn Huệ",
    "city": "Thành phố Hồ Chí Minh",
    "zip": "700000",
    "phone": "+84 28 0000 0000",
    "email": "contact@fmcg-simulator.example.test",
    "vat": "0312345678",
})
env.cr.commit()
print({"model": "res.company", "id": company.id, "name": company.name})
