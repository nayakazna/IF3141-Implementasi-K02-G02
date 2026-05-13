from odoo import api, fields, models


def _notify_user(env, title, message):
    user = env.user
    notify = getattr(user, "notify_info", None)
    if notify:
        try:
            notify(message, title=title, sticky=False)
        except TypeError:
            try:
                notify(message, title)
            except Exception:
                pass


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

    @api.model_create_multi
    def create(self, vals_list):
        leads = super().create(vals_list)
        for vals in vals_list:
            if {
                "x_raw_specs",
                "x_technical_notes",
                "x_simulator_type",
                "x_simulator_type_id",
            }.intersection(vals):
                _notify_user(self.env, "Kebutuhan Proyek Tersimpan", "Kebutuhan proyek berhasil disimpan.")
                break
        return leads

    def write(self, vals):
        result = super().write(vals)
        if {
            "x_raw_specs",
            "x_technical_notes",
            "x_simulator_type",
            "x_simulator_type_id",
        }.intersection(vals):
            _notify_user(self.env, "Kebutuhan Proyek Tersimpan", "Kebutuhan proyek berhasil disimpan.")
        return result
