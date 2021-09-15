# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    oxigesti_bind_ids = fields.One2many(
        comodel_name='oxigesti.product.category',
        inverse_name='odoo_id',
        string='Oxigesti Bindings',
    )
