import logging
import random
from itertools import product
from odoo import Command, api, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

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

    @api.model
    def cron_inventory_confirm_receipts(self, limit=100):
        inventory_user = self.env.ref(
            "fmcg_workflow_simulator.user_inventory_user_simulator"
        )

        # Chi lấy những Stock.picking có state là draft và code = incoming
        pickings = self.env["stock.picking"].search([
            ("picking_type_id.code", "=", "incoming"),
            ("state", "=", "draft"),
            ("move_ids", "!=", False),
        ], limit=limit)

        for picking in pickings:
            try:
                with self.env.cr.savepoint():
                    picking.with_user(inventory_user).action_confirm()
            except Exception:
                _logger.exception("Cannot confirm picking %s", picking.name)

        return True

    @api.model
    def cron_inventory_prepare_receipts(self, limit=50):
        inventory_user = self.env.ref(
            "fmcg_workflow_simulator.user_inventory_user_simulator"
        )

        pickings = self.env["stock.picking"].search([
            ("picking_type_id.code", "=", "incoming"),
            ("state", "=", "assigned"),
            ("move_ids.picked", "=", False),
        ], limit=limit)

        for picking in pickings:
        # Chọn ngẫu nhiên một kịch bản nhận hàng cho mỗi picking:
        # - 50% nhận đủ
        # - 15% nhận thiếu
        # - 5% không nhận được hàng
        # - 5% nhận dư
        # - 25% nhận hỗn hợp

            picking_scenario = random.choices(
                ["full", "partial", "none", "excess", "mixed"],
                weights=[50, 15, 5, 5, 25],
                k=1,
            )[0]

            try:
                moves = picking.move_ids.filtered(
                    lambda move: (
                        move.state not in ("done", "cancel")
                        and not move.picked
                    )
                )

                for move in moves:
                    scenario = picking_scenario

                    # Mỗi sản phẩm có tình trạng nhận hàng riêng.
                    if picking_scenario == "mixed":
                        scenario = random.choices(
                            ["full", "partial", "none"],
                            weights=[60, 30, 10],
                            k=1,
                        )[0]

                    demand = move.product_uom_qty

                    if scenario == "full":
                        received_qty = demand
                    elif scenario == "partial":
                        received_qty = demand * random.uniform(0.50, 0.99)
                    elif scenario == "none":
                        received_qty = 0
                    else:
                        received_qty = demand * random.uniform(1.01, 1.20)

                    received_qty = float_round(
                        received_qty,
                        precision_rounding=move.product_uom.rounding,
                    )

                    move.with_user(inventory_user).write({
                        "quantity": received_qty,
                        # True nghĩa là dòng đã được kiểm nhận,
                        # kể cả kết quả nhận thực tế bằng 0.
                        "picked": True,
                    })

                    _logger.info(
                        "Receipt %s, product %s: %s, demand=%s, received=%s",
                        picking.name,
                        move.product_id.display_name,
                        scenario,
                        demand,
                        received_qty,
                    )

            except Exception:
                _logger.exception(
                    "Cannot prepare receipt %s with scenario %s",
                    picking.name,
                    scenario,
                )

        return True

    @api.model
    def cron_inventory_prepare_multi_lot_receipts(self, limit=30):
        inventory_user = self.env.ref(
            "fmcg_workflow_simulator.user_inventory_user_simulator"
        )

        pickings = self.env["stock.picking"].search([
            ("picking_type_id.code", "=", "incoming"),
            ("state", "=", "assigned"),
            ("move_ids.picked", "=", False),
        ], limit=limit)

        for picking in pickings:
            try:
                moves = picking.move_ids.filtered(
                    lambda move: (
                        move.state not in ("done", "cancel")
                        and not move.picked
                        and move.product_id.tracking == "lot"
                        and not move.move_line_ids
                    )
                )

                for move in moves:
                    received_qty = move.product_uom_qty
                    rounding = move.product_uom.rounding

                    # Không đủ lượng để chia tối thiểu hai lô.
                    if received_qty < rounding * 2:
                        continue

                    lot_count = random.randint(2, min(4, int(
                        received_qty / rounding
                    )))

                    remaining_qty = received_qty

                    for index in range(1, lot_count + 1):
                        if index == lot_count:
                            lot_qty = remaining_qty
                        else:
                            max_qty = (
                                remaining_qty
                                - rounding * (lot_count - index)
                            )
                            lot_qty = float_round(
                                random.uniform(rounding, max_qty),
                                precision_rounding=rounding,
                            )

                        lot = self.env["stock.lot"].with_user(
                            inventory_user
                        ).create({
                            "name": (
                                f"FMCG-{picking.name.replace('/', '-')}"
                                f"-{move.id}-{index}"
                            ),
                            "product_id": move.product_id.id,
                            "company_id": picking.company_id.id,
                        })

                        self.env["stock.move.line"].with_user(
                            inventory_user
                        ).create({
                            "move_id": move.id,
                            "picking_id": picking.id,
                            "product_id": move.product_id.id,
                            "product_uom_id": move.product_uom.id,
                            "lot_id": lot.id,
                            "quantity": lot_qty,
                            "location_id": move.location_id.id,
                            "location_dest_id": move.location_dest_id.id,
                            "picked": True,
                        })

                        remaining_qty -= lot_qty

                    _logger.info(
                        "Receipt %s, product %s split into %s lots",
                        picking.name,
                        move.product_id.display_name,
                        lot_count,
                    )

            except Exception:
                _logger.exception(
                    "Cannot prepare multi-lot receipt %s",
                    picking.name,
                )

        return True