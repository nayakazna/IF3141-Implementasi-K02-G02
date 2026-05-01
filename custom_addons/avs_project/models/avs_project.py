from odoo import models, fields, api

class AvsStage(models.Model):
    _inherit = 'project.task.type'    
    x_is_closed = fields.Boolean(string="Tahap Selesai?", default=False) # field buat stage yg beres

class AvsProject(models.Model):
    _inherit = 'project.project'

    x_overall_progress = fields.Float(string="Total Progress (%)", compute="_compute_overall_progress", store=True)

    @api.depends('task_ids.x_progress_percent')
    def _compute_overall_progress(self):
        for project in self:
            tasks = project.task_ids
            if tasks:
                project.x_overall_progress = sum(tasks.mapped('x_progress_percent')) / len(tasks)
            else:
                project.x_overall_progress = 0.0

class AvsTask(models.Model):
    _inherit = 'project.task'

    x_progress_percent = fields.Float(string="Progress (%)", compute="_compute_task_progress", store=True)
    x_weight = fields.Integer(string="Bobot Task (Points)", default=1)
    x_is_overloaded = fields.Boolean(string="Overload?", compute="_compute_is_overloaded")

    @api.depends('stage_id.x_is_closed', 'child_ids.stage_id.x_is_closed')
    def _compute_task_progress(self):
        for task in self:
            if task.stage_id.x_is_closed:
                task.x_progress_percent = 100.0
            elif task.child_ids:
                total_sub = len(task.child_ids)
                done_sub = len(task.child_ids.filtered(lambda s: s.stage_id.x_is_closed))
                task.x_progress_percent = (done_sub / total_sub) * 100
            else:
                task.x_progress_percent = 0.0

    @api.depends('user_ids', 'user_ids.x_current_load', 'user_ids.x_max_capacity')
    def _compute_is_overloaded(self):
        for task in self:
            overloaded = False
            for user in task.user_ids:
                if user.x_current_load > user.x_max_capacity:
                    overloaded = True
                    break
            task.x_is_overloaded = overloaded

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