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
        # chỉ lấy đối tác là nhà cung cấp
        partners = [False] + list(self.env["res.partner"].search([('supplier_rank', '>', 0)]))

        # chọn picking type bằng incoming, vì đây là tạo recept!
        picking_types = [False] + list(self.env["stock.picking.type"].search([("code", "=", "incoming")]))

        # chỉ lấy kho là của nhà cung câp
        locations = [False] + list(self.env["stock.location"].search([("usage", "=", "supplier")]))

        # chuyển đến kho nội bộ công ty
        location_dest_id = [False] + list(self.env["stock.location"].search([("usage", "=", "internal")]))

        # chưa cần giả lập đơn sale vì hiện tại chưa cần
        # sales = [False] + list(self.env["sale.order"].search([]))
        # Chỉ lấy user thuộc nhân viên kho
        users = [False] + list(self.env["res.users"].search([("group_ids", "in", self.env.ref("stock.group_stock_user").id)]))

        # Chỉ chọn những product có thể mua và có thể nhập kho (tiêu hao hoặc lưu kho)
        products = list(self.env["product.product"].search([
                                                            ("purchase_ok", "=", True),
                                                            ("type", "in", ["product", "consu"])
                                                            ]))

        final_location_ids = [location.id if location else False for location in location_dest_id]

        # Sinh từng tổ hợp, không đưa toàn bộ tích Descartes vào bộ nhớ.
        combinations = list(product(
            partners, picking_types, locations, location_dest_id, 
            # sales,
            users
        ))
        random.shuffle(combinations)
        
        for partner, stock_picking_type, stock_location, stock_location_dest, user in combinations:
            if not stock_picking_type or not stock_location or not stock_location_dest:
                continue

            self.env["stock.picking"].with_user(inventory_user).create({
                "partner_id": partner.id if partner else False,
                "picking_type_id": stock_picking_type.id if stock_picking_type else False,
                "location_id": stock_location.id if stock_location else False,
                "location_dest_id": stock_location_dest.id if stock_location_dest else False,
                "user_id": user.id if user else False,
                "move_ids": [
                    Command.create({
                        "product_id": random_product.id,
                        "product_uom": random.choice(self.env['stock.move'].new({'product_id': random_product.id}).allowed_uom_ids.ids),
                        "product_uom_qty": random.randint(1, 10),
                        "quantity": random.randint(0, 10),
                        "location_final_id": random.choice(final_location_ids) if final_location_ids else False,
                        "location_id": stock_location.id if stock_location else False,
                        "location_dest_id": stock_location_dest.id if stock_location_dest else False,
                    })
                    for random_product in random.sample(
                        products, random.randint(1, min(5, len(products)))
                    )
                ],
            })
            self.env.cr.commit()
        return True
