import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError

from datetime import timedelta
import random

_logger = logging.getLogger(__name__)


class FmcgSimulatorRun(models.AbstractModel):
    _name = "fmcg.simulator.run"
    _description = "FMCG Workflow Simulator Service"

    @api.model
    def _get_simulator_user(self, login):
        user = self.env["res.users"].sudo().search([
            ("login", "=", login),
            ("active", "=", True),
        ], limit=1)
        if not user:
            _logger.warning("FMCG Simulator: Không tìm thấy user %s", login)
        return user

    @api.model
    def cron_master(self):
        """Orchestrator chạy tuần tự các kịch bản mới."""
        self.cron_inventory_replenish_new()
        self.cron_purchase_user_process()
        # self.cron_purchase_manager_approve()
        # self.cron_inventory_user_receipt()
        # self.cron_inventory_user_transfer()

    @api.model
    def cron_inventory_replenish_new(self):
        """1. Quản lý kho: Kiểm kê định kỳ & Báo thiếu."""
        user = self._get_simulator_user("inventory.manager.simulator")
        if not user: return False
        self = self.with_user(user).with_company(user.company_id)
        
        _, category = self._get_replenishment_master_data()
        other_categories = self.env["product.category"].search([
            ("name", "in", [
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
        orderpoints = self._get_replenishment_orderpoints(category | other_categories)
        if orderpoints:
            _logger.info("Inventory Manager: Kích hoạt Procurement cho %d rules", len(orderpoints))
            
            # 1. Tối ưu: Chỉ lấy ID lớn nhất hiện tại (tránh load hàng ngàn ID vào RAM nếu DB lớn)
            po_max_id = self.env['purchase.order'].search([], order='id desc', limit=1).id or 0
            picking_max_id = self.env['stock.picking'].search([], order='id desc', limit=1).id or 0
            mo_max_id = self.env['mrp.production'].search([], order='id desc', limit=1).id or 0 if 'mrp.production' in self.env else 0
            
            # 2. Gọi hàm gốc
            orderpoints.action_replenish()
            
            # 3. Lấy các record mới được tạo ra (id > max_id cũ)
            new_pos = self.env['purchase.order'].search([('id', '>', po_max_id)])
            new_pickings = self.env['stock.picking'].search([('id', '>', picking_max_id)])
            
            _logger.info("--- KẾT QUẢ ACTION_REPLENISH ---")
            if new_pos:
                _logger.info("- Tạo mới %d Purchase Orders: %s", len(new_pos), new_pos.mapped('name'))

                # Tự động tạo Activity giao việc cho Purchase User
                purchase_user = self._get_simulator_user("purchase.user.simulator")
                if purchase_user:
                    # Sửa lỗi AccessError: Dùng sudo() vì Inventory Manager không có quyền tạo activity trên form Purchase
                    new_pos.sudo().activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=purchase_user.id,
                        summary='Chốt đơn mua hàng (Tự động từ Simulator)',
                        note='Hệ thống tự động báo thiếu kho và sinh ra yêu cầu mua hàng này.'
                    )
                    _logger.info("- Đã giao %d task (Activities) cho %s", len(new_pos), purchase_user.login)

            if new_pickings:
                _logger.info("- Tạo mới %d Stock Pickings: %s", len(new_pickings), new_pickings.mapped('name'))
            
            if 'mrp.production' in self.env:
                new_mos = self.env['mrp.production'].search([('id', '>', mo_max_id)])
                if new_mos:
                    _logger.info("- Tạo mới %d Manufacturing Orders: %s", len(new_mos), new_mos.mapped('name'))
                
                if not new_pos and not new_pickings and not new_mos:
                    _logger.info("- Không tạo ra record PO/MO/Picking nào (Tồn kho có thể đã đủ hoặc lỗi Route).")
            else:
                if not new_pos and not new_pickings:
                    _logger.info("- Không tạo ra record PO/Picking nào (Tồn kho có thể đã đủ hoặc lỗi Route).")
            _logger.info("--------------------------------")
            
        return True

    @api.model
    def cron_purchase_user_process(self):
        """2. NV Mua hàng: Xử lý RFQ được simulator giao."""
        user = self._get_simulator_user("purchase.user.simulator")
        if not user:
            return False

        self = self.with_user(user).with_company(user.company_id)
        todo_type = self.env.ref("mail.mail_activity_data_todo")
        task_summary = "Chốt đơn mua hàng (Tự động từ Simulator)"

        # 1. Tìm các Activity đang pending của user này
        activities = self.env["mail.activity"].search([
            ("res_model", "=", "purchase.order"),
            ("user_id", "=", user.id),
            ("activity_type_id", "=", todo_type.id),
            ("summary", "=", task_summary),
        ])

        if not activities:
            return True

        # 2. Giả lập delay: Chỉ lấy các task đã được tạo cách đây ít nhất 30 phút
        # Chọn một mốc delay ngẫu nhiên từ 15 phút đến 4 tiếng cho lần chạy này
        random_minutes = random.randint(15, 240)
        delay_threshold = fields.Datetime.now() - timedelta(minutes=random_minutes)
        due_activities = activities.filtered(lambda a: a.create_date and a.create_date <= delay_threshold)

        if not due_activities:
            _logger.info("Purchase User: Có %d task nhưng chưa đến hạn xử lý (cần đợi thêm để giả lập delay).", len(activities))
            return True

        rfqs = self.env["purchase.order"].search([
            ("id", "in", due_activities.mapped("res_id")),
            ("company_id", "=", user.company_id.id),
            ("state", "in", ["draft", "sent"]),
        ], order="id", limit=50)

        confirmed = waiting = failed = 0

        for rfq in rfqs:
            # Click xác nhận đơn hàng
            rfq.button_confirm()

            # Đóng task của Purchase User
            tasks = due_activities.filtered(
                lambda activity: activity.res_id == rfq.id
            )
            tasks.action_feedback(
                feedback="Đã xử lý RFQ. Trạng thái: %s." % rfq.state
            )

            # 3. Phân nhánh xử lý sau khi xác nhận
            if rfq.state == 'to approve':
                waiting += 1
                _logger.info("Purchase User: %s -> Cần Quản lý duyệt (to approve)", rfq.name)
                
                # Sinh task cho Purchase Manager (Giả lập chuyển bước)
                manager = self._get_simulator_user("purchase.manager.simulator")
                if manager:
                    rfq.sudo().activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=manager.id,
                        summary='Duyệt đơn mua hàng (Tự động từ Simulator)',
                        note='Đơn hàng vượt ngân sách, cần Quản lý mua hàng phê duyệt.'
                    )
            elif rfq.state in ['purchase', 'done']:
                confirmed += 1
                _logger.info("Purchase User: %s -> Xác nhận thành công (purchase)", rfq.name)
            else:
                failed += 1
                _logger.info("Purchase User: %s -> Không thành công, trạng thái: %s", rfq.name, rfq.state)

        _logger.info(
            "Purchase User: Đã xác nhận %d, chờ duyệt %d, lỗi %d",
            confirmed, waiting, failed,
        )
        return True

    @api.model
    def cron_purchase_manager_approve(self):
        """3. QL Mua hàng: Duyệt đơn vượt ngân sách (nếu có)."""
        user = self._get_simulator_user("purchase.manager.simulator")
        if not user: return False
        self = self.with_user(user).with_company(user.company_id)
        
        to_approve_rfqs = self.env["purchase.order"].search([("state", "=", "to approve")])
        if to_approve_rfqs:
            _logger.info("Purchase Manager: Duyệt %d đơn hàng", len(to_approve_rfqs))
            to_approve_rfqs.button_approve()
        return True

    @api.model
    def cron_inventory_user_receipt(self):
        """4. NV Kho: Nhận hàng vật lý từ NCC."""
        user = self._get_simulator_user("inventory.user.simulator")
        if not user: return False
        self = self.with_user(user).with_company(user.company_id)
        
        pickings = self.env["stock.picking"].search([
            ("picking_type_id.code", "=", "incoming"),
            ("state", "=", "assigned")
        ])
        
        if pickings:
            _logger.info("Inventory User: Nhận %d chuyến hàng", len(pickings))
            for picking in pickings:
                for move in picking.move_ids:
                    if not move.quantity:
                        move.quantity = move.product_uom_qty
                picking.with_context(skip_sanity_check=True, skip_backorder=True).button_validate()
        return True

    @api.model
    def cron_inventory_user_transfer(self):
        """5. NV Kho: Xuất hàng đi sản xuất."""
        user = self._get_simulator_user("inventory.user.simulator")
        if not user: return False
        self = self.with_user(user).with_company(user.company_id)
        
        # Chỉ quét các phiếu xuất nội bộ tự sinh (nếu cấu hình Reordering Rules MTO) 
        # đang ở trạng thái Ready để validate.
        pickings = self.env["stock.picking"].search([
            ("picking_type_id.code", "=", "internal"),
            ("state", "=", "assigned")
        ], limit=10)
        
        if pickings:
            _logger.info("Inventory User: Xuất %d chuyến hàng nội bộ", len(pickings))
            for picking in pickings:
                for move in picking.move_ids:
                    if not move.quantity:
                        move.quantity = move.product_uom_qty
                picking.with_context(skip_sanity_check=True, skip_backorder=True).button_validate()
        return True

    @api.model
    def cron_generate_raw_material_rfq(self):
        """(Deprecated) Hàm cũ."""
        execution_user = self.env["res.users"].sudo().search([
            ("login", "=", "purchase.simulator"),
            ("active", "=", True),
        ], limit=1)

        self = self.with_user(execution_user).with_company(
            execution_user.company_id
        )
        
        # Vẫn cần lấy category để filter đúng các orderpoints của "Nguyên liệu đa ngành"
        _, category = self._get_replenishment_master_data()
        orderpoints = self._get_raw_material_orderpoints(category)
        
        if orderpoints:
            _logger.info("Kích hoạt Odoo Procurement Engine cho %d quy tắc tái cung ứng", len(orderpoints))
            # Gọi action giao diện của Odoo theo yêu cầu
            orderpoints.action_replenish()
        else:
            _logger.info("Không có quy tắc tái cung ứng nào cần xử lý.")
            
        # Cron job không nhất thiết phải return danh sách recordset như code cũ, return True là đủ
        return True


    @api.model
    def _get_replenishment_master_data(self):
        """Resolve the simulator vendor and raw-material category."""
        company = self.env.company
        vendors = self.env["res.partner"].search([
            ("supplier_rank", ">", 0),
            ("company_id", "in", [False, company.id]),
        ])
        if not vendors:
            raise UserError(_(
                "No vendors found. Run the partner master-data seed "
                "before running this scheduled action."
            ))

        raw_material_category = self.env["product.category"].search([
            ("name", "=", "Nguyên liệu đa ngành"),
        ], limit=1)
        if not raw_material_category:
            raise UserError(_(
                "The raw-material product category was not found. Run the "
                "FMCG catalog seed before running this scheduled action."
            ))

        return vendors, raw_material_category

    @api.model
    def _get_raw_material_orderpoints(self, category):
        """Use active policies for purchasable raw materials in this company."""
        return self.env["stock.warehouse.orderpoint"].search([
            ("company_id", "=", self.env.company.id),
            ("product_id.active", "=", True),
            ("product_id.purchase_ok", "=", True),
            ("product_id.is_storable", "=", True),
            ("product_id.categ_id", "child_of", category.id),
        ], order="id")
