# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools.translate import _


class ProductProduct(models.Model):
    _inherit = "product.product"

    _sql_constraints = [
        (
        'barcode_uniq', 'unique(company_id, barcode)', _("A barcode can only be assigned to one product per company!")),
    ]
