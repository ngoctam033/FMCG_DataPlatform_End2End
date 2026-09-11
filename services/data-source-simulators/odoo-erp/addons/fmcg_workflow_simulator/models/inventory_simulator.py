import logging
import random
from itertools import product
from odoo import Command, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class FmcgInventorySimulator(models.AbstractModel):
    _inherit = "fmcg.simulator.run"

    @api.model
    def cron_inventory_create_receipt_request(self):
        inventory_user = self.env.ref(
            "fmcg_workflow_simulator.user_inventory_user_simulator"
        )
        partners = [False] + list(self.env["res.partner"].search([]))
        picking_types = [False] + list(self.env["stock.picking.type"].search([]))
        locations = [False] + list(self.env["stock.location"].search([]))
        location_dest_id = locations.copy()
        sales = [False] + list(self.env["sale.order"].search([]))
        users = [False] + list(self.env["res.users"].search([]))
        products = list(self.env["product.product"].search([]))
        final_location_ids = [location.id if location else False for location in locations]
        packaging_uom_ids = [False] + self.env["uom.uom"].search([]).ids

        # Sinh từng tổ hợp, không đưa toàn bộ tích Descartes vào bộ nhớ.
        combinations = product(
            partners, picking_types, locations, location_dest_id, sales, users
        )
        for partner, stock_picking_type, stock_location, stock_location_dest, sale, user in random.sample(
                        list(combinations), min(50, len(partners) * len(picking_types) * len(locations) * len(location_dest_id) * len(sales) * len(users))):
            if not stock_picking_type or not stock_location or not stock_location_dest:
                continue

            if not sale and not products:
                raise UserError("Không có sản phẩm để tạo dòng hàng ngẫu nhiên.")

            self.env["stock.picking"].with_user(inventory_user).create({
                "partner_id": partner.id if partner else False,
                "picking_type_id": stock_picking_type.id if stock_picking_type else False,
                "location_id": stock_location.id if stock_location else False,
                "location_dest_id": stock_location_dest.id if stock_location_dest else False,
                "origin": sale.name if sale else False,
                "user_id": user.id if user else False,
                "move_ids": [
                    Command.create({
                        "product_id": line.product_id.id,
                        "product_uom": line.product_uom_id.id,
                        "product_uom_qty": line.product_uom_qty,
                        "quantity": random.randint(0, 10),
                        "location_final_id": final_location_id,
                        "packaging_uom_id": packaging_uom_id,
                        "location_id": stock_location.id if stock_location else False,
                        "location_dest_id": stock_location_dest.id if stock_location_dest else False,
                        "sale_line_id": line.id,
                    })
                    for line in (sale.order_line if sale else [])
                    if line.product_id and not line.display_type
                    for final_location_id, packaging_uom_id in product(
                        final_location_ids, packaging_uom_ids
                    )
                ] if sale else [
                    Command.create({
                        "product_id": random_product.id,
                        "product_uom": random_product.uom_id.id,
                        "product_uom_qty": random.randint(1, 10),
                        "quantity": random.randint(0, 10),
                        "location_final_id": final_location_id,
                        "packaging_uom_id": packaging_uom_id,
                        "location_id": stock_location.id if stock_location else False,
                        "location_dest_id": stock_location_dest.id if stock_location_dest else False,
                    })
                    for random_product in random.sample(
                        products, random.randint(1, min(3, len(products)))
                    )
                    for final_location_id, packaging_uom_id in product(
                        final_location_ids, packaging_uom_ids
                    )
                ],
            })
            self.env.cr.commit()
        return True
