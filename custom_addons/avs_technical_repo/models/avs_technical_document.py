import base64
import binascii

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AvsTechnicalDocument(models.Model):
    _name = "avs.technical.document"
    _description = "AVS Technical Document"
    _order = "upload_date desc, id desc"

    name = fields.Char(string="Document Title", required=True)
    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        required=True,
        ondelete="cascade",
    )
    doc_type = fields.Selection(
        [
            ("dro", "Document Requirement Outline (DRO)"),
            ("cad", "Computer-Aided Design (CAD)"),
            ("uat", "User Acceptance Test (UAT)"),
            ("other", "Other Technical Document"),
        ],
        string="Document Type",
        required=True,
    )
    file_data = fields.Binary(string="File", required=True, attachment=True)
    file_name = fields.Char(string="File Name")
    version = fields.Integer(string="Version", default=1, readonly=True)
    uploaded_by = fields.Many2one(
        comodel_name="res.users",
        string="Uploaded By",
        default=lambda self: self.env.user,
        readonly=True,
    )
    upload_date = fields.Datetime(
        string="Upload Date",
        default=fields.Datetime.now,
        readonly=True,
    )
    notes = fields.Text(string="Revision Notes")
    active = fields.Boolean(string="Active", default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            file_data = vals.get("file_data")
            if not file_data:
                raise ValidationError("File tidak boleh kosong.")

            try:
                decoded = base64.b64decode(file_data)
            except (binascii.Error, ValueError) as exc:
                raise ValidationError("Format file tidak valid.") from exc

            if not decoded:
                raise ValidationError("Ukuran file harus lebih dari 0 byte.")

            vals["uploaded_by"] = self.env.user.id
            vals["upload_date"] = fields.Datetime.now()

            if vals.get("project_id") and vals.get("doc_type") and vals.get("name"):
                latest = self.with_context(active_test=False).search(
                    [
                        ("project_id", "=", vals["project_id"]),
                        ("doc_type", "=", vals["doc_type"]),
                        ("name", "=", vals["name"]),
                    ],
                    order="version desc, id desc",
                    limit=1,
                )
                vals["version"] = latest.version + 1 if latest else 1

        return super().create(vals_list)
