from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    x_technical_document_count = fields.Integer(
        string="Technical Documents",
        compute="_compute_technical_document_count",
    )

    def _compute_technical_document_count(self):
        counts = self.env["avs.technical.document"].with_context(active_test=False).read_group(
            [("project_id", "in", self.ids)],
            ["project_id"],
            ["project_id"],
        )
        count_map = {item["project_id"][0]: item["project_id_count"] for item in counts}
        for project in self:
            project.x_technical_document_count = count_map.get(project.id, 0)

    def action_view_technical_documents(self):
        self.ensure_one()
        action = self.env.ref("avs_technical_repo.action_avs_technical_document").read()[0]
        action["domain"] = [("project_id", "=", self.id)]
        action["context"] = {
            "default_project_id": self.id,
            "search_default_project_id": self.id,
        }
        return action
