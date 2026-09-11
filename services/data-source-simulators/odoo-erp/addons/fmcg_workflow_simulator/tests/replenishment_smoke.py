"""Run through Odoo shell on an installed module; all fixture writes roll back.

This is a diagnostic script, not an automatically discovered Odoo test suite.
"""
from unittest.mock import patch

try:
    simulator = env['fmcg.simulator.run']
    company = env.company
    warehouse = env['stock.warehouse'].search([('company_id', '=', company.id)], limit=1)
    assert warehouse, 'A warehouse is required'
    category = env['product.category'].create({'name': 'TEST replenishment category'})
    vendor = env['res.partner'].create({'name': 'TEST replenishment vendor', 'supplier_rank': 1})
    product = env['product.product'].create({
        'name': 'TEST replenishment material', 'is_storable': True,
        'purchase_ok': True, 'categ_id': category.id,
    })
    seller = env['product.supplierinfo'].create({
        'partner_id': vendor.id, 'product_tmpl_id': product.product_tmpl_id.id,
        'price': 7, 'min_qty': 0, 'company_id': company.id,
    })
    rule = env['stock.warehouse.orderpoint'].create({
        'product_id': product.id, 'location_id': warehouse.lot_stock_id.id,
        'product_min_qty': 100, 'product_max_qty': 500, 'trigger': 'manual',
    })
    quant = env['stock.quant']
    quant._update_available_quantity(product, rule.location_id, 100)
    with patch.object(type(simulator), '_get_replenishment_master_data', return_value=(vendor, category)):
        assert not simulator.cron_generate_raw_material_rfq(), 'At Min: no RFQ'
        quant._update_available_quantity(product, rule.location_id, -30)
        orders = simulator.cron_generate_raw_material_rfq()
        assert len(orders) == 1 and orders.state == 'draft'
        line = orders.order_line
        assert line.product_qty == 430, line.product_qty
        assert line.orderpoint_id == rule
        assert line.location_final_id == rule.location_id
        assert not simulator.cron_generate_raw_material_rfq(), 'Pending RFQ must prevent duplicate'
        orders.button_cancel()
        replacement = simulator.cron_generate_raw_material_rfq()
        assert len(replacement) == 1, 'Cancelled RFQ must not cover demand'
        replacement.button_confirm()
        assert not simulator.cron_generate_raw_material_rfq(), 'Confirmed incoming purchase covers demand'
        # A different stock location must not be covered by the first rule's PO.
        location = env['stock.location'].create({
            'name': 'TEST separate replenishment location', 'usage': 'internal',
            'location_id': warehouse.view_location_id.id, 'company_id': company.id,
        })
        second_rule = env['stock.warehouse.orderpoint'].create({
            'product_id': product.id, 'location_id': location.id,
            'product_min_qty': 100, 'product_max_qty': 500, 'trigger': 'manual',
        })
        assert simulator._get_replenishment_quantity(second_rule) == 500
        seller.min_qty = 600
        selected, quantity = simulator._select_replenishment_supplier(second_rule, vendor, 500)
        assert selected == seller and quantity == 600, quantity
        seller.date_end = '2000-01-01'
        selected, quantity = simulator._select_replenishment_supplier(second_rule, vendor, 500)
        assert not selected, 'Expired vendor price must not be used'
    print('PASS: Min boundary, shortage, draft deduplication, cancellation, confirmed incoming, location isolation, MOQ, expired price')
finally:
    env.cr.rollback()
