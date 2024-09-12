# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class WordPressIrChecksum(models.Model):
    _name = "wordpress.ir.checksum"
    _inherit = "wordpress.binding"
    _inherits = {"ir.checksum": "odoo_id"}
    _description = "WordPress Ir Checksum Binding"

    odoo_id = fields.Many2one(
        comodel_name="ir.checksum",
        string="Ir Checksum",
        required=True,
        ondelete="cascade",
    )
    wordpress_idchecksum = fields.Integer(
        string="ID Checksum",
        readonly=True,
    )
    wordpress_source_url = fields.Char(
        string="Source URL",
        readonly=True,
    )
