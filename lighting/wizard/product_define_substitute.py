# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LightingProductDefineSubstitute(models.TransientModel):
    """
    This wizard will allow to assign multiple substitutes at once
    """
    _name = "lighting.product.define.substitute"
    _description = "Define substitutes"

    @api.multi
    def define_substitute(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        products = self.env['lighting.product'].browse(active_ids)

        for product in products:
            substitute_ids = products.filtered(lambda x: x.id!=product.id)

            if product.substitute_ids:
                substitute_ids = substitute_ids.filtered(lambda x: x.id not in (product.substitute_ids.mapped('id')))

            if substitute_ids:
                product.substitute_ids = [(4, x.id, False) for x in substitute_ids]


