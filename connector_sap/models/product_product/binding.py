# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    sap_bind_ids = fields.One2many(
        comodel_name='sap.product.product',
        inverse_name='odoo_id',
        string='SAP Bindings',
    )


class ProductProductBinding(models.Model):
    _name = 'sap.product.product'
    _inherit = 'sap.binding'
    _inherits = {'product.product': 'odoo_id'}

    odoo_id = fields.Many2one(comodel_name='product.product',
                              string='Product',
                              required=True,
                              ondelete='cascade')

    sap_sku = fields.Char(string='SKU')

    _sql_constraints = [
        (
            "sap_product_external_uniq",
            "unique(backend_id, sap_sku)",
            "A binding already exists with the same External (SAP) ID.",
        ),
    ]
