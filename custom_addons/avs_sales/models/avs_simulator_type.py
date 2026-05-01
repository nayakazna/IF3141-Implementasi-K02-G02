from odoo import fields, models


class AvsSimulatorType(models.Model):
    _name = "avs.simulator.type"
    _description = "AVS Simulator Type"
    _order = "sequence, name, id"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(string="Active", default=True)
