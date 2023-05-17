# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    wordpress_bind_ids = fields.One2many(
        comodel_name="wordpress.ir.attachment",
        inverse_name="odoo_id",
        string="WordPress Bindings",
    )
