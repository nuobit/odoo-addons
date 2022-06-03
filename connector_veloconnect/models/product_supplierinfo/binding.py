# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    veloconnect_bind_ids = fields.One2many(
        comodel_name='veloconnect.product.supplierinfo',
        inverse_name='odoo_id',
        string='Veloconnect Bindings',
    )


class ProductSupplierinfoBinding(models.Model):
    _name = 'veloconnect.product.supplierinfo'
    _inherit = 'veloconnect.binding'
    _inherits = {'product.supplierinfo': 'odoo_id'}

    odoo_id = fields.Many2one(comodel_name='product.supplierinfo',
                              string='supplierinfo line',
                              required=True,
                              ondelete='cascade')

    veloconnect_seller_id = fields.Char(string='Veloconnect SellersItemIdentificationID', required=True)
    veloconnect_minimum_quantity = fields.Integer(string='Veloconnect MinimumQuantity', required=True)

    veloconnect_product_tmpl_id = fields.Many2one(comodel_name='veloconnect.product.template',
                                                  string='Veloconnect Product',
                                                  required=True,
                                                  ondelete='cascade',
                                                  index=True)

    _sql_constraints = [
        (
            "vp_external_uniq",
            "unique(backend_id, veloconnect_seller_id,veloconnect_minimum_quantity)",
            "A binding already exists with the same External (veloconnect) ID.",
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            veloconnect_product_id = vals['veloconnect_product_tmpl_id']
            binding = self.env['veloconnect.product.template'].browse(veloconnect_product_id)
            with binding.backend_id.work_on(binding._name) as work:
                binder = work.component(usage='binder')
                vals['product_tmpl_id'] = binder.unwrap_binding(binding).id
                vals['backend_id'] = binding.backend_id.id
        binding = super().create(vals_list)
        # FIXME triggers function field
        # The amounts (amount_total, ...) computed fields on 'product.template' are
        # not triggered when magento.product.supplierinfo are created.
        # It might be a v8 regression, because they were triggered in
        # v7. Before getting a better correction, force the computation
        # by writing again on the line.
        # line = binding.odoo_id
        # line.write({'price_unit': line.price_unit})
        return binding
