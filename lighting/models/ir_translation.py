# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import re


class IrTranslation(models.Model):
    _inherit = 'ir.translation'

    @api.constrains('value', 'source')
    def _update_product_description(self):
        model, field = self.name.split(',')
        depends_fields = self.env['lighting.product'] \
            .fields_get(['description'], ['depends'])['description']['depends']
        for depend in depends_fields:
            dpath = re.split('\.', depend)
            if len(dpath) > 1:
                dmodelpath, dfield = dpath[:-1], dpath[-1]
                dobj = self.env['lighting.product']
                for dm in dmodelpath:
                    dobj = dobj[dm]
                dmodel = dobj._name
                if (model, field) == (dmodel, dfield):
                    products = self.env['lighting.product'].search([
                        ('.'.join(dmodelpath), 'in', [self.res_id])
                    ])
                    products._compute_description()
                    break
