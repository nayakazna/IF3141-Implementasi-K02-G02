from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AvsAftersalesReport(models.Model):
    _name = "avs.aftersales.report"
    _description = "AVS Aftersales Report"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "report_date desc, id desc"

    name = fields.Char(string="Report Number", required=True, copy=False, default=lambda self: _("New"), tracking=True)
    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        related="project_id.partner_id",
        store=True,
        readonly=True,
    )
    report_date = fields.Datetime(string="Report Date", default=fields.Datetime.now, required=True, tracking=True)
    reporter_id = fields.Many2one(
        comodel_name="res.users",
        string="Reported By",
        default=lambda self: self.env.user,
        readonly=True,
        tracking=True,
    )
    priority = fields.Selection(
        [
            ("0", "Low"),
            ("1", "Normal"),
            ("2", "High"),
            ("3", "Urgent"),
        ],
        string="Priority",
        default="1",
        tracking=True,
    )
    description = fields.Text(string="Complaint / Report", required=True, tracking=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("recorded", "Recorded"),
            ("forwarded", "Forwarded"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
    forwarded_to_id = fields.Many2one(
        comodel_name="res.users",
        string="Forward To",
        tracking=True,
    )
    can_forward = fields.Boolean(compute="_compute_can_forward")
    forwarded_by_id = fields.Many2one(
        comodel_name="res.users",
        string="Forwarded By",
        readonly=True,
        tracking=True,
    )
    forwarded_date = fields.Datetime(string="Forwarded Date", readonly=True, tracking=True)
    forwarded_note = fields.Text(string="Forwarding Note")
    resolution_note = fields.Text(string="Resolution Note", tracking=True)
    attachment = fields.Binary(string="Attachment", attachment=True)
    attachment_name = fields.Char(string="Attachment Name")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code("avs.aftersales.report") or _("New")
        records = super().create(vals_list)
        for record in records:
            record.message_post(body=_("Aftersales report recorded."))
        return records

    @api.depends("state", "forwarded_to_id")
    def _compute_can_forward(self):
        is_sales = self.env.user.has_group("avs_project.group_avs_sales")
        for report in self:
            report.can_forward = (
                report.state not in ("done", "cancel")
                and (
                    is_sales
                    or (report.state == "forwarded" and report.forwarded_to_id == self.env.user)
                )
            )

    def action_record(self):
        for report in self:
            if report.state != "draft":
                continue
            report.state = "recorded"
            report.message_post(body=_("Report has been recorded."))

    def action_forward(self):
        for report in self:
            if report.state not in ("draft", "recorded", "forwarded"):
                raise UserError(_("Only draft, recorded, or forwarded reports can be forwarded."))
            if not report.forwarded_to_id:
                raise ValidationError(_("Please choose a user to forward the report to."))
            is_sales = self.env.user.has_group("avs_project.group_avs_sales")
            is_assigned_forwarded_user = report.state == "forwarded" and report.forwarded_to_id == self.env.user
            if not (is_sales or is_assigned_forwarded_user):
                raise UserError(_("Only Sales or the current forwarded user can forward this report."))
            report_sudo = report.sudo()
            report_sudo.write(
                {
                    "state": "forwarded",
                    "forwarded_by_id": self.env.user.id,
                    "forwarded_date": fields.Datetime.now(),
                }
            )
            report_sudo.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=report.forwarded_to_id.id,
                summary=_("Follow up aftersales report"),
                note=report.forwarded_note or report.description,
            )
            report_sudo.message_post(
                body=_("Report forwarded to %s.") % report.forwarded_to_id.display_name,
                partner_ids=report.forwarded_to_id.partner_id.ids,
            )

    def action_mark_done(self):
        for report in self:
            report.state = "done"
            report.message_post(body=_("Report has been marked as done."))

    def action_cancel(self):
        for report in self:
            report.state = "cancel"
            report.message_post(body=_("Report has been cancelled."))

    def action_reset_draft(self):
        for report in self:
            report.state = "draft"
            report.message_post(body=_("Report has been reset to draft."))
