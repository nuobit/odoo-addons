# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields


class ProductTemplateBinding(models.Model):
    _name = 'veloconnect.product.template'
    _inherit = 'veloconnect.binding'
    _inherits = {'product.template': 'odoo_id'}

    odoo_id = fields.Many2one(comodel_name='product.template',
                              string='Product',
                              required=True,
                              ondelete='cascade',
                              )
    veloconnect_seller_item_id = fields.Char(string="Veloconnect SellersItemIdentificationID", required=True)

    # veloconnect_ean = fields.Char(string='Veloconnect StandardItemIdentification', required=True)
    veloconnect_hash = fields.Char(string='Veloconnect Hash', required=True)
    veloconnect_description = fields.Char(string='Veloconnect Description')
    veloconnect_price = fields.Float(string='Veloconnect RecommendedRetailPrice', required=True)
    veloconnect_uom = fields.Char(string='Veloconnect quantityUnitCode', required=True)
    # veloconnect_seller_ids = fields.One2many(
    #     comodel_name="veloconnect.product.supplierinfo",
    #     inverse_name="veloconnect_product_tmpl_id",
    # )

    _sql_constraints = [
        (
            "vp_external_uniq",
            "unique(backend_id, veloconnect_seller_item_id)",
            "A binding already exists with the same External (veloconnect) ID.",
        ),
    ]

    def import_products(self, backend_record=None):
        """ Prepare the batch import of products modified on Veloconnect"""
        domain = []
        self.env['veloconnect.product.template'].import_batch(
            backend_record=backend_record, domain=domain)

        return True

    def resync_import(self):
        # raise NotImplementedError("Resync not implemented yet")
        for record in self:
            with record.backend_id.work_on(record._name) as work:
                binder = work.component(usage='binder')
                relation = binder.unwrap_binding(self)
            func = record.import_record
            if record.env.context.get('connector_delay'):
                func = record.import_record.delay

            func(record.backend_id, relation)

        return True
