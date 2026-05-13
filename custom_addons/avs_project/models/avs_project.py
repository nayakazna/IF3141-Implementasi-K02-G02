from odoo import models, fields, api
from odoo.exceptions import ValidationError


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

class AvsStage(models.Model):
    _inherit = 'project.task.type'

    x_is_closed = fields.Boolean(string="Tahap Selesai?", default=False)
    x_stage_progress = fields.Float(
        string="Progress Tahap (%)",
        default=0.0,
        help="Persentase progres untuk task yang berada di tahap ini (0 - 100).",
    )
    x_exclude_from_progress = fields.Boolean(
        string="Kecualikan dari Progress Proyek",
        default=False,
        help="Jika aktif, task pada tahap ini tidak ikut dihitung ke progress proyek.",
    )

    @api.constrains('x_stage_progress')
    def _check_stage_progress_range(self):
        for stage in self:
            if stage.x_stage_progress < 0.0 or stage.x_stage_progress > 100.0:
                raise ValidationError("Progress tahap harus berada di rentang 0 sampai 100.")

class AvsProject(models.Model):
    _inherit = 'project.project'

    x_overall_progress = fields.Float(string="Total Progress (%)", compute="_compute_overall_progress", store=True)

    @api.depends(
        'task_ids.parent_id',
        'task_ids.x_weight',
        'task_ids.x_progress_percent',
        'task_ids.stage_id.x_exclude_from_progress',
    )
    def _compute_overall_progress(self):
        for project in self:
            tasks = project.task_ids.filtered(
                lambda t: not t.parent_id and not t.stage_id.x_exclude_from_progress
            )
            if tasks:
                weighted_total = 0.0
                total_weight = 0.0
                fallback_progress = 0.0

                for task in tasks:
                    progress = task.x_progress_percent
                    weight = max(task.x_weight, 0)
                    fallback_progress += progress
                    weighted_total += progress * weight
                    total_weight += weight

                if total_weight > 0:
                    project.x_overall_progress = weighted_total / total_weight
                else:
                    project.x_overall_progress = fallback_progress / len(tasks)
            else:
                project.x_overall_progress = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        projects = super().create(vals_list)
        _notify_user(self.env, "Proyek Berhasil Dibuat", "Proyek berhasil dibuat.")
        return projects

    def write(self, vals):
        result = super().write(vals)
        if "active" in vals and not vals.get("active"):
            _notify_user(self.env, "Status Proyek Diperbarui", "Status proyek berhasil diperbarui.")
        else:
            _notify_user(self.env, "Proyek Berhasil Diperbarui", "Perubahan proyek berhasil disimpan.")
        return result

class AvsTask(models.Model):
    _inherit = 'project.task'

    x_progress_percent = fields.Float(string="Progress (%)", compute="_compute_task_progress", store=True)
    x_weight = fields.Integer(string="Bobot Task (Points)", default=1)
    x_is_overloaded = fields.Boolean(string="Overload?", compute="_compute_is_overloaded")

    @api.constrains('x_weight')
    def _check_non_negative_weight(self):
        for task in self:
            if task.x_weight < 0:
                raise ValidationError("Bobot task tidak boleh bernilai negatif.")

    @api.depends(
        'stage_id.x_stage_progress',
        'child_ids.x_progress_percent',
        'child_ids.x_weight',
        'child_ids.stage_id.x_exclude_from_progress',
    )
    def _compute_task_progress(self):
        for task in self:
            subtasks = task.child_ids.filtered(lambda s: not s.stage_id.x_exclude_from_progress)
            if subtasks:
                weighted_total = 0.0
                total_weight = 0.0
                fallback_progress = 0.0

                for subtask in subtasks:
                    progress = subtask.x_progress_percent
                    weight = max(subtask.x_weight, 0)
                    fallback_progress += progress
                    weighted_total += progress * weight
                    total_weight += weight

                if total_weight > 0:
                    task.x_progress_percent = weighted_total / total_weight
                else:
                    task.x_progress_percent = fallback_progress / len(subtasks)
            else:
                task.x_progress_percent = task.stage_id.x_stage_progress or 0.0

    @api.depends('user_ids', 'user_ids.x_current_load', 'user_ids.x_max_capacity')
    def _compute_is_overloaded(self):
        for task in self:
            overloaded = False
            for user in task.user_ids:
                if user.x_current_load > user.x_max_capacity:
                    overloaded = True
                    break
            task.x_is_overloaded = overloaded

    def write(self, vals):
        result = super().write(vals)
        if vals:
            _notify_user(self.env, "Tugas Berhasil Diperbarui", "Perubahan tugas berhasil disimpan.")
        return result

class ResUsers(models.Model):
    _inherit = 'res.users'

    x_max_capacity = fields.Integer(string="Kapasitas Maksimal (Points)", default=10)
    x_current_load = fields.Integer(string="Beban Kerja Saat Ini", compute="_compute_current_load")

    def _compute_current_load(self):
        for user in self:
            # cari yg blom selesai
            active_tasks = self.env['project.task'].search([
                ('user_ids', 'in', user.id),
                ('stage_id.x_is_closed', '=', False)
            ])
            user.x_current_load = sum(active_tasks.mapped('x_weight'))
