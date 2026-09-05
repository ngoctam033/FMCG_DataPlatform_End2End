"""Configure simulator product vendors; execute with ``odoo shell``.

Run after 01_seed_fmcg_catalog.py and 02_seed_partners.py, in the company
used by inventory.manager.simulator. Re-run after reseeding the catalog.
Only the 22 explicit SKUs below are managed. No RFQs are created or changed.

Prices are SIMULATION values: current company standard cost per product UoM,
in company currency. MOQ=10 and lead time=7 days match the catalog seed.
Specialist priority=1; general supplier priority=100. Water remains general.
The catalog contains no dairy input or logistics service to assign.

Existing general-vendor pins on mapped reordering rules are cleared so native
vendor selection can use the specialist and retain the general as fallback.
Other explicit vendor pins are rejected rather than silently overwritten.
Ambiguous price tiers/shared-company data are rejected for manual review.

Preview without persisting (inside a fresh Odoo shell):
    env = env(context=dict(env.context, supplier_seed_dry_run=True))
    exec(open('/path/to/14_seed_product_supplierinfo.py').read())

The native cron currently includes only the raw-material category, not
packaging/trading products. This script does not broaden that cron's scope.
"""

SUPPLIER_PRODUCTS = {
    "SUP-GENERAL": ("RM-PURIFIED-WATER",),
    "SUP-INGREDIENTS": (
        "RM-WHEAT-FLOUR", "RM-SEASONING", "RM-POTATO",
        "RM-VEG-OIL", "RM-CHILI-PASTE",
    ),
    "SUP-CHEMICAL": ("RM-CLEANING-BASE",),
    "SUP-PACKAGING": (
        "PM-BOTTLE-GENERIC", "PM-CAN-330", "PM-POUCH-GENERIC",
    ),
    "SUP-TRADING": (
        "TRADE-TISSUE-10", "TRADE-TOOTHPASTE-180", "TRADE-SHAMPOO-650",
        "TRADE-SHOWER-GEL-500", "TRADE-HANDWASH-500",
        "TRADE-FLOOR-CLEANER-1L", "TRADE-FABRIC-SOFTENER-2L",
        "TRADE-COFFEE-3IN1-20", "TRADE-BISCUIT-300", "TRADE-FISH-SAUCE-750",
    ),
    "SUP-FROZEN": ("FROZEN-DUMPLING-500", "FROZEN-ICECREAM-450"),
}


def seed_supplier_master(env):
    """Apply and verify in caller's transaction; never commit here."""
    company = env.company
    Partner = env["res.partner"]
    Product = env["product.product"]
    Seller = env["product.supplierinfo"]
    Orderpoint = env["stock.warehouse.orderpoint"]
    vendors = {}
    plans = []
    seen = set()

    # Resolve all prerequisites before any writes. Do not silently pick the
    # first duplicate SKU/vendor reference or alter another company's records.
    for ref, codes in SUPPLIER_PRODUCTS.items():
        vendor = Partner.search([
            ("ref", "=", ref), ("supplier_rank", ">", 0),
            ("company_id", "in", [False, company.id]),
        ])
        if len(vendor) != 1:
            raise ValueError(f"Expected one active vendor {ref}; found {len(vendor)}. Run/review 02_seed_partners.py.")
        vendors[ref] = vendor
        for code in codes:
            if code in seen:
                raise ValueError(f"Duplicate SKU mapping: {code}")
            seen.add(code)
            product = Product.search([
                ("default_code", "=", code), ("purchase_ok", "=", True),
                ("company_id", "in", [False, company.id]),
            ])
            if len(product) != 1 or product.product_tmpl_id.product_variant_count != 1:
                raise ValueError(f"Expected one active single-variant product {code}. Run/review 01_seed_fmcg_catalog.py.")
            if product.standard_price <= 0:
                raise ValueError(f"{code}: positive simulation cost required in {company.name}.")
            rules = Orderpoint.search([
                ("product_id", "=", product.id), ("company_id", "=", company.id),
            ])
            for rule in rules:
                if rule.supplier_id and rule.supplier_id.partner_id not in (vendor | vendors["SUP-GENERAL"]):
                    raise ValueError(f"{code}: orderpoint {rule.id} pins another vendor; review before seeding.")
            for target in vendor | vendors["SUP-GENERAL"]:
                rows = Seller.search([
                    ("product_tmpl_id", "=", product.product_tmpl_id.id),
                    ("partner_id", "=", target.id),
                    ("company_id", "in", [False, company.id]),
                ])
                if len(rows) > 1 or (rows and (
                    not rows.company_id or rows.product_id or rows.date_start
                    or rows.date_end or rows.min_qty != 10
                )):
                    raise ValueError(f"{code}/{target.ref}: shared, variant-specific, dated or tiered prices require manual review.")
                plans.append((product, target, rows, 1 if target == vendor else 100))

    created = updated = cleared_pins = 0
    for product, vendor, row, sequence in plans:
        values = {
            "partner_id": vendor.id,
            "product_tmpl_id": product.product_tmpl_id.id,
            "product_id": False, "company_id": company.id,
            "currency_id": company.currency_id.id,
            "product_uom_id": product.uom_id.id,
            "price": product.standard_price, "discount": 0,
            "min_qty": 10, "delay": 7, "sequence": sequence,
        }
        if row:
            row.write(values)
            updated += 1
        else:
            Seller.create(values)
            created += 1

    for ref, codes in SUPPLIER_PRODUCTS.items():
        for code in codes:
            product = next(p for p, _, _, _ in plans if p.default_code == code)
            if ref != "SUP-GENERAL":
                general_pins = Orderpoint.search([
                    ("product_id", "=", product.id), ("company_id", "=", company.id),
                    ("supplier_id.partner_id", "=", vendors["SUP-GENERAL"].id),
                ])
                cleared_pins += len(general_pins)
                general_pins.write({"supplier_id": False})
            # Exercise this checkout's native selection, including competing
            # pre-existing vendor rows. Unexpected selection aborts the seed.
            selected = product._select_seller(quantity=10, uom_id=product.uom_id)
            if selected.partner_id != vendors[ref]:
                raise ValueError(f"{code}: Odoo selected {selected.partner_id.display_name}, expected {vendors[ref].display_name}; review competing vendor prices.")
            print(f"{code} -> {ref}")

    return {
        "company": company.name, "products": len(seen),
        "created": created, "updated": updated,
        "general_vendor_pins_cleared": cleared_pins,
    }


if "env" in globals():
    # A failed validation rolls back the entire seed, including when called
    # through exec() in an interactive shell that stays open after the error.
    class _PreviewComplete(Exception):
        pass

    dry_run = env.context.get("supplier_seed_dry_run", False)
    try:
        with env.cr.savepoint():
            result = seed_supplier_master(env)
            if dry_run:
                raise _PreviewComplete()
    except _PreviewComplete:
        print(dict(result, dry_run=True, committed=False))
    else:
        env.cr.commit()
        print(dict(result, dry_run=False, committed=True))
