from odoo import api, fields, models
from odoo.exceptions import ValidationError

class AvsMaterial(models.Model):
    _name = "avs.material"
    _description = "AVS Material Inventory"
    _order = "name asc"

    name = fields.Char(string="Nama Material", required=True)
    code = fields.Char(string="Kode Part", required=True, copy=False)
    unit = fields.Selection(
        [
            ("pcs", "Pcs"),
            ("meter", "Meter"),
            ("kg", "Kilogram"),
            ("liter", "Liter"),
            ("set", "Set"),
        ],
        string="Satuan",
        required=True,
        default="pcs",
    )
    stock_qty = fields.Float(string="Stok Tersedia", default=0.0)
    min_stock_qty = fields.Float(string="Stok Minimum", default=0.0)
    description = fields.Text(string="Deskripsi")
    is_low_stock = fields.Boolean(
        string="Stok Menipis?",
        compute="_compute_is_low_stock",
        store=True,
    )

    _sql_constraints = [
        ("code_unique", "UNIQUE(code)", "Kode part harus unik."),
    ]

    @api.depends("stock_qty", "min_stock_qty")
    def _compute_is_low_stock(self):
        for rec in self:
            rec.is_low_stock = rec.stock_qty < rec.min_stock_qty

    @api.constrains("stock_qty", "min_stock_qty")
    def _check_non_negative(self):
        for rec in self:
            if rec.stock_qty < 0:
                raise ValidationError("Stok tidak boleh bernilai negatif.")
            if rec.min_stock_qty < 0:
                raise ValidationError("Stok minimum tidak boleh bernilai negatif.")