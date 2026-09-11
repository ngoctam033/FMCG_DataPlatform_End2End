"""Run via Odoo shell after catalog/partner seeds; always roll back.

Tests the real ORM and native vendor selection without invoking procurement.
The seed is loaded without its shell entrypoint, so it cannot commit.
"""
from pathlib import Path

seed_path = Path("/mnt/extra-addons/fmcg_workflow_simulator/scripts/14_seed_product_supplierinfo.py")
namespace = {}
exec(compile(seed_path.read_text(), str(seed_path), "exec"), namespace)
seed = namespace["seed_supplier_master"]

try:
    user = env["res.users"].search([
        ("login", "=", "inventory.manager.simulator"),
    ])
    assert len(user) == 1, "Expected one inventory manager simulator"
    test_env = env(context=dict(env.context, allowed_company_ids=[user.company_id.id]))
    Seller = test_env["product.supplierinfo"]
    original_count = Seller.search_count([])
    first = seed(test_env)
    first_rows = Seller.search([]).read([
        "partner_id", "product_tmpl_id", "product_id", "company_id",
        "currency_id", "product_uom_id", "price", "discount",
        "min_qty", "delay", "sequence",
    ])
    second = seed(test_env)
    second_rows = Seller.search([]).read(list(first_rows[0].keys()))
    assert first["products"] == second["products"] == 22
    assert second["created"] == 0, "Rerun must not create duplicate prices"
    assert second["general_vendor_pins_cleared"] == 0
    assert first_rows == second_rows, "Rerun must preserve supplier master values"
    assert Seller.search_count([]) == original_count + first["created"]
    print({"test": "supplier_master_smoke", "result": "PASS", "first": first, "second": second})
finally:
    env.cr.rollback()
    print("Rolled back all supplier master test changes.")
