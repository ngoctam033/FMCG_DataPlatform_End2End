import logging

from odoo import api, fields, models

import random

_logger = logging.getLogger(__name__)


class FmcgSimulatorRun(models.AbstractModel):
    _name = "fmcg.simulator.run"
    _description = "FMCG Workflow Simulator Service"

    @api.model
    def cron_master(self):
        """Mô phỏng vòng đời tái cung ứng theo từng sản phẩm đang thiếu."""
        master_self = self
        inventory_manager = self.env["res.users"].sudo().search([("login", "=", "inventory.manager.simulator"), ("active", "=", True)], limit=1)
        purchase_user = self.env["res.users"].sudo().search([("login", "=", "purchase.user.simulator"),("active", "=", True)], limit=1)
        purchase_manager = self.env["res.users"].sudo().search([("login", "=", "purchase.manager.simulator"),("active", "=", True)], limit=1)
        inventory_user = self.env["res.users"].sudo().search([("login", "=", "inventory.user.simulator"),("active", "=", True)], limit=1)

        inventory_runner = master_self.with_user(
            inventory_manager
        ).with_company(inventory_manager.company_id)

        category = inventory_runner.env["product.category"].search([("name", "=", "Nguyên liệu đa ngành")], limit=1)

        other_categories = inventory_runner.env["product.category"].search([("name", "in", [
                "Hàng thương mại",
                "Hàng đông lạnh",
                "Bao bì đa ngành",
                "Chăm sóc cá nhân",
                "Chăm sóc gia đình",
                "Thực phẩm ăn liền",
                "Bánh kẹo & Snack",
                "Gia vị",
            ]),
        ])
        categories = category | other_categories

        orderpoints = inventory_runner.env[
            "stock.warehouse.orderpoint"
        ].search([
            ("company_id", "=", inventory_manager.company_id.id),
            ("product_id.active", "=", True),
            ("product_id.purchase_ok", "=", True),
            ("product_id.is_storable", "=", True),
            ("product_id.categ_id", "child_of", categories.ids),
            ("qty_to_order", ">", 0),
            "|",
            ("snoozed_until", "=", False),
            ("snoozed_until", "<=", fields.Date.today()),
        ], order="id")


        # Lấy các sản phẩm cần cung ứng
        missing_product_records = orderpoints

        #  Duyệt qua các sản phẩm cần cung ứng để thực hiện thao tác
        for orderpoint in missing_product_records:
            product = orderpoint.product_id

            # yêu cầu tạo RFQ từ orderpoint và bắt giá trị trả về
            notification = orderpoint.action_replenish()

            # Phân tích dictionary để lấy ID của RFQ (nằm ở cuối đường link)
            url = notification.get("params", {}).get("links", [{}])[0].get("url", "")
            rfq_id = int(url.split("/")[-1]) if url else 0
            # Lấy thẳng bản ghi RFQ từ ID
            rfqs = inventory_runner.env["purchase.order"].browse(rfq_id) if rfq_id else inventory_runner.env["purchase.order"]

            for rfq in rfqs:
                rfq.sudo().activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=purchase_user.id,
                    summary="Chốt đơn mua hàng (Tự động từ Simulator)",
                    note=(
                        "RFQ được tạo từ nhu cầu thiếu hàng của sản phẩm %s."
                        % product.display_name
                    ),
                )

                purchase_runner = rfq.with_user(
                    purchase_user
                ).with_company(purchase_user.company_id)
                purchase_action = random.choices(
                    ["confirm", "skip"],
                    weights=[90, 10],
                    k=1,
                )[0]

                if purchase_action == "skip":
                    continue

                purchase_runner.button_confirm()
                
                # Đi từ RFQ sang activity_ids, sau đó dùng hàm filtered để lọc
                purchase_tasks = rfq.sudo().activity_ids.filtered(
                    lambda activity: 
                        activity.user_id.id == purchase_user.id 
                        and activity.summary == "Chốt đơn mua hàng (Tự động từ Simulator)"
                )
                if purchase_tasks:
                    purchase_tasks.action_feedback(
                        feedback="Đã xác nhận RFQ."
                    )

                if purchase_runner.state == "to approve":
                    purchase_runner.sudo().activity_schedule(
                        "mail.mail_activity_data_todo",
                        user_id=purchase_manager.id,
                        summary=(
                            "Duyệt đơn mua hàng (Tự động từ Simulator)"
                        ),
                        note=(
                            "Đơn mua sản phẩm %s cần được phê duyệt."
                            % product.display_name
                        ),
                    )

                    manager_action = random.choices(
                        ["approve", "reject", "skip"],
                        weights=[70, 20, 10],
                        k=1,
                    )[0]
                    manager_runner = purchase_runner.with_user(
                        purchase_manager
                    ).with_company(purchase_manager.company_id)

                    if manager_action == "approve":
                        manager_runner.button_approve()
                    elif manager_action == "reject":
                        manager_runner.button_cancel()
                    else:
                        continue

                    purchase_runner = manager_runner

                    manager_tasks = master_self.env[
                        "mail.activity"
                    ].sudo().search([
                        ("res_model", "=", "purchase.order"),
                        ("res_id", "=", rfq.id),
                        ("user_id", "=", purchase_manager.id),
                        ("summary", "=", (
                            "Duyệt đơn mua hàng "
                            "(Tự động từ Simulator)"
                        )),
                    ])
                    if manager_tasks:
                        feedback = (
                            "Đã duyệt đơn hàng."
                            if manager_action == "approve"
                            else "Đã từ chối đơn hàng."
                        )
                        manager_tasks.action_feedback(feedback=feedback)

                if purchase_runner.state not in ["purchase", "done"]:
                    continue

                incoming_pickings = purchase_runner.picking_ids.filtered(
                    lambda picking: (
                        picking.picking_type_id.code == "incoming"
                        and picking.state == "assigned"
                    )
                )
                for picking in incoming_pickings:
                    inventory_picking = picking.with_user(
                        inventory_user
                    ).with_company(inventory_user.company_id)
                    for move in inventory_picking.move_ids:
                        if not move.quantity:
                            move.quantity = move.product_uom_qty
                    validate_action = inventory_picking.button_validate()
                    
                    # Bắt đầu thêm code từ đây để in ra log
                    _logger.info("========== KẾT QUẢ VALIDATE ACTION ==========")
                    _logger.info(validate_action)
                    _logger.info("=============================================")

                internal_pickings = master_self.with_user(
                    inventory_user
                ).with_company(inventory_user.company_id).env[
                    "stock.picking"
                ].search([
                    ("picking_type_id.code", "=", "internal"),
                    ("state", "=", "assigned"),
                    ("move_ids.product_id", "=", product.id),
                ], limit=10)

                for picking in internal_pickings:
                    for move in picking.move_ids.filtered(
                        lambda stock_move: stock_move.product_id == product
                    ):
                        if not move.quantity:
                            move.quantity = move.product_uom_qty
                    picking.with_context(
                        skip_sanity_check=True,
                        skip_backorder=True,
                    ).button_validate()

        return True
