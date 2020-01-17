# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.constrains('default_code')
    def _check_default_code(self):
        for record in self:
            if record.default_code:
                default_code = self.with_context(active_test=False).search([
                    ('product_tmpl_id.company_id', '=', record.product_tmpl_id.company_id.id),
                    ('default_code', '=', record.default_code),
                    ('id', '!=', record.id),
                ], limit=1)

                if default_code:
                    raise ValidationError(
                        _("Error! The Default Code %s already exists. Check also the archived ones." %
                          record.default_code)
                    )
