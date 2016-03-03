from openerp import models, fields, api, _

class dt_product_template(models.Model):
    _inherit = "product.template"
    _order = 'website_published desc, public_categ_sequence, default_code' #, website_sequence desc, name'


    public_categ_sequence = fields.Integer(compute='_compute_public_categ_sequence', store=True)

    @api.depends('public_categ_ids.sequence')
    def _compute_public_categ_sequence(self):
        for record in self:
            if record.public_categ_ids:
                record.public_categ_sequence = record.public_categ_ids[0].sequence


