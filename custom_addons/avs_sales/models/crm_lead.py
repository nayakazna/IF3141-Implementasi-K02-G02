from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    x_raw_specs = fields.Html(string="Spesifikasi Mentah Klien", sanitize=True)
    x_technical_notes = fields.Html(string="Catatan Teknis Awal", sanitize=True)
    x_simulator_type = fields.Selection(
        [
            ("flight", "Flight Simulator"),
            ("driving", "Driving Simulator"),
            ("marine", "Ship Simulator"),
        ],
        string="Simulator Type (Legacy)",
        help="Field lama untuk kompatibilitas data. Gunakan Simulator Type baru.",
    )
    x_simulator_type_id = fields.Many2one(
        comodel_name="avs.simulator.type",
        string="Simulator Type",
        ondelete="set null",
    )
