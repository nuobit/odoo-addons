from openerp import models, fields, api, _

import openerp.addons.website_sale.controllers.main as main

class dt_product_template(models.Model):
    _inherit = "product.template"

    public_categ_sequence = fields.Integer(compute='_compute_public_categ_sequence', store=True)
    public_default_code = fields.Char(compute='_compute_public_default_code', store=True)

    @api.depends('public_categ_ids.sequence')
    def _compute_public_categ_sequence(self):
        for record in self:
            if record.public_categ_ids:
                record.public_categ_sequence = record.public_categ_ids[0].sequence

    @api.depends('product_variant_ids.default_code')
    def _compute_public_default_code(self):
        for record in self:
            if record.product_variant_ids:
                record.public_default_code = record.product_variant_ids[0].default_code




class website_sale(main.website_sale):
    def _get_search_order(self, post):
        res = super(website_sale, self)._get_search_order(post)
        # OrderBy will be parsed in orm and so no direct sql injection
        return 'website_published desc,public_categ_sequence, public_default_code'