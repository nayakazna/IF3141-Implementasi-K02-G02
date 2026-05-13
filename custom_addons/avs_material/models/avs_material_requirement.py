from odoo import api, fields, models
from odoo.exceptions import ValidationError


def _notify_user(env, title, message):
    user = env.user
    partner = user.partner_id
    if not partner:
        return

    bus = env["bus.bus"]
    payload = {
        "title": title,
        "message": message,
        "sticky": False,
    }
    try:
        bus._sendone(partner, "display_notification", payload)
    except Exception:
        notify = getattr(user, "notify_info", None)
        if notify:
            try:
                notify(message, title=title, sticky=False)
            except TypeError:
                try:
                    notify(message, title)
                except Exception:
                    pass


class AvsMaterialRequirement(models.Model):
    _name = "avs.material.requirement"
    _description = "AVS Material Requirement"
    _order = "create_date desc, id desc"

    task_id = fields.Many2one(
        comodel_name="project.task",
        string="Task",
        required=True,
        ondelete="cascade",
    )
    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        related="task_id.project_id",
        store=True,
        readonly=True,
    )
    material_id = fields.Many2one(
        comodel_name="avs.material",
        string="Material",
        required=True,
        ondelete="restrict",
    )
    qty_required = fields.Float(string="Jumlah Dibutuhkan", required=True)
    status = fields.Selection(
        [
            ("available", "Available"),
            ("pending_procurement", "Pending Procurement"),
        ],
        string="Status",
        default="available",
        readonly=True,
    )
    procurement_request_id = fields.Many2one(
        comodel_name="avs.procurement.request",
        string="Procurement Request",
        readonly=True,
    )
    notes = fields.Text(string="Catatan")

    @api.constrains("qty_required")
    def _check_qty_required(self):
        for rec in self:
            if rec.qty_required <= 0:
                raise ValidationError("Jumlah kebutuhan harus lebih dari 0.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            qty = vals.get("qty_required")
            if qty is None or qty <= 0:
                raise ValidationError("Jumlah kebutuhan harus lebih dari 0.")

            task_id = vals.get("task_id")
            if not task_id:
                raise ValidationError("Task harus diisi.")

            material_id = vals.get("material_id")
            if material_id:
                material = self.env["avs.material"].browse(material_id)
                if material.stock_qty >= qty:
                    vals["status"] = "available"
                else:
                    task = self.env["project.task"].browse(task_id)
                    if not task.project_id:
                        raise ValidationError("Task harus terhubung ke proyek.")

                    req = self.env["avs.procurement.request"].create({
                        "material_id": material_id,
                        "project_id": task.project_id.id,
                        "qty_requested": qty,
                    })
                    vals["status"] = "pending_procurement"
                    vals["procurement_request_id"] = req.id
        records = super().create(vals_list)
        for rec in records:
            if rec.status == "pending_procurement":
                _notify_user(
                    self.env,
                    "Kebutuhan Material Pending",
                    "Kebutuhan material tercatat dan menunggu pengadaan.",
                )
            else:
                _notify_user(
                    self.env,
                    "Kebutuhan Material Tercatat",
                    "Kebutuhan material berhasil dicatat.",
                )
        return records


class ProjectTask(models.Model):
    _inherit = "project.task"

    x_material_requirement_ids = fields.One2many(
        comodel_name="avs.material.requirement",
        inverse_name="task_id",
        string="Material Requirements",
    )
