from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AvsProcurementRequest(models.Model):
    _name = "avs.procurement.request"
    _description = "AVS Procurement Request"
    _order = "request_date desc, id desc"

    name = fields.Char(
        string="Nomor Pengajuan",
        readonly=True,
        copy=False,
        default="New",
    )
    material_id = fields.Many2one(
        comodel_name="avs.material",
        string="Material",
        required=True,
        ondelete="restrict",
    )
    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Proyek",
        required=True,
        ondelete="restrict",
    )
    qty_requested = fields.Float(string="Jumlah Diminta", required=True)
    requested_by = fields.Many2one(
        comodel_name="res.users",
        string="Diajukan Oleh",
        default=lambda self: self.env.user,
        readonly=True,
    )
    request_date = fields.Datetime(
        string="Tanggal Pengajuan",
        default=fields.Datetime.now,
        readonly=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Diajukan"),
            ("approved", "Disetujui"),
            ("received", "Diterima"),
            ("rejected", "Ditolak"),
        ],
        string="Status",
        default="draft",
        readonly=True,
    )
    received_date = fields.Datetime(string="Tanggal Diterima", readonly=True)
    qty_received = fields.Float(string="Jumlah Diterima")
    notes = fields.Text(string="Catatan")

    @api.constrains("qty_requested")
    def _check_qty(self):
        for rec in self:
            if rec.qty_requested <= 0:
                raise ValidationError("Jumlah yang diminta harus lebih dari 0.")

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError("Hanya draft yang bisa diajukan.")
            rec.state = "submitted"

    def action_approve(self):
        for rec in self:
            if rec.state != "submitted":
                raise ValidationError("Hanya pengajuan yang sudah disubmit yang bisa disetujui.")
            rec.state = "approved"

    def action_receive(self):
        for rec in self:
            if rec.state != "approved":
                raise ValidationError("Hanya pengajuan yang sudah disetujui yang bisa diterima.")
            if rec.qty_received <= 0:
                raise ValidationError("Jumlah diterima harus lebih dari 0.")
            rec.material_id.stock_qty += rec.qty_received
            rec.received_date = fields.Datetime.now()
            rec.state = "received"

    def action_reject(self):
        for rec in self:
            if rec.state not in ("submitted", "draft"):
                raise ValidationError("Status tidak bisa ditolak.")
            rec.state = "rejected"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "avs.procurement.request"
                ) or "New"
        return super().create(vals_list)