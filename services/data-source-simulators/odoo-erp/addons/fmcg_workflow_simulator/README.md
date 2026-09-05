# FMCG Workflow Simulator

Odoo 19 service for creating draft raw-material RFQs from replenishment needs.

## Workflow

The master cron runs every five minutes after the module is upgraded. It calls
`cron_generate_raw_material_rfq`, which:

1. Resolves the simulator vendor and the `Nguyên liệu đa ngành` category.
2. Finds active replenishment rules for purchasable, storable raw materials in
   the current company, including child categories.
3. Uses Odoo's orderpoint forecast, forecast horizon, Min/Max and replenishment
   units to calculate shortages. The forecast includes outstanding RFQs and
   confirmed incoming/outgoing movements according to native Odoo rules.
4. Selects a valid vendor price for the product/variant and date, respecting
   minimum order quantities and purchase units.
5. Creates one draft RFQ per eligible rule, with `SIM-RFQ-*` origin,
   orderpoint linkage and the rule's final destination. Native purchase helpers
   prepare prices, currency conversion, taxes, discounts and planned dates.

No shortage means no RFQ. No valid supplier price means the rule is skipped
with a warning. Missing vendor/category is a configuration error. No matching
replenishment rules results in a logged zero-rule run. The entry point returns
an Odoo purchase-order recordset, possibly empty or containing multiple RFQs.

## Configuration

Install/upgrade this module with its `purchase_stock` dependency. Seed the
simulator vendor, raw-material catalog and supplier prices. Configure active
`stock.warehouse.orderpoint` records per product/location with Min, Max and
optional replenishment units. The simulator ignores manual quantity overrides.
Supplier minimums and rounding can make the resulting purchase exceed Max.

The existing `13_seed_stock_warehouse_orderpoint.py` creates policies with
`trigger=auto`. Choose one replenishment owner: if the master simulator owns
these policies, configure them as manual to avoid competing with Odoo's native
automatic scheduler. This refactor does not change existing policy triggers.
Outstanding RFQs prevent sequential duplicate replenishment; concurrent manual
runs or another scheduler are not serialized by this implementation.

The master cron is enabled in XML; the legacy standalone RFQ cron remains
disabled. RFQs are not confirmed automatically. Only the scheduler user's
current company is processed. Restart Odoo and upgrade this module to apply
code and dependency changes.

## Verification

From the repository root, with the module already installed:

```bash
docker compose exec -T odoo /entrypoint.sh odoo shell \
  -c /etc/odoo/odoo.conf -d fmcg_erp --no-http \
  < services/data-source-simulators/odoo-erp/addons/fmcg_workflow_simulator/tests/replenishment_smoke.py
```

The diagnostic script creates isolated fixtures and rolls back its transaction
in `finally`. It checks threshold behavior, calculated quantity, pending RFQs,
cancelled RFQs, confirmed incoming purchases, separate locations, supplier
minimum quantities and expired prices.
