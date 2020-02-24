# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models, api, _


def seo_preview(title, url, description):
    template = """
        <div style="font-family:arial,sans-serif;max-width:600px;">
            <ul class="list-unstyled">
                %s
            </ul>
        </div >
    """
    template_title = '<li style="margin-bottom:0;color:#1a0dab;font-size:18px;">%s</li>'
    template_url = '<li style="margin-bottom:0;color:#006621;font-size:14px;">%s</li>'
    template_description = '<li style="margin-bottom:0;color:#545454;font-size:small;">%s</li>'

    preview = []
    if title:
        preview.append(template_title % title)
    if url:
        preview.append(template_url % url)
    if description:
        preview.append(template_description % description)

    meta_preview = False
    if preview:
        meta_preview = template % ''.join(preview)

    return meta_preview


class LightingProduct(models.Model):
    _inherit = 'lighting.product'

    website_published = fields.Boolean('Published on Website', copy=False)

    @api.multi
    def website_publish_button(self):
        self.ensure_one()
        return self.write({'website_published': not self.website_published})

    @api.onchange('state_marketing')
    def onchange_state_marketing(self):
        if self.state_marketing in ('D', 'H'):
            if self.website_published:
                self.website_published = False

    seo_title = fields.Char(string='Meta title', translate=True)
    seo_url = fields.Char(string='URL')
    seo_description = fields.Text(string='Meta description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword',
                                       relation='lighting_product_seo_keyword_rel',
                                       column1='product_id', column2='keyword_id', string='Keywords')

    meta_title_length = fields.Integer(string='Meta title length', compute='_compute_lengths', readonly=True)
    meta_description_length = fields.Integer(string='Meta description length', compute='_compute_lengths',
                                             readonly=True)

    @api.depends('seo_title', 'seo_description')
    def _compute_lengths(self):
        for rec in self:
            if rec.seo_title:
                rec.meta_title_length = len(rec.seo_title)
            if rec.seo_description:
                rec.meta_description_length = len(rec.seo_description)

    meta_preview = fields.Char(string='Preview', compute='_compute_preview', readonly=True)

    @api.depends('seo_title', 'seo_url', 'seo_description')
    def _compute_preview(self):
        for rec in self:
            rec.meta_preview = seo_preview(rec.seo_title, rec.seo_url, rec.seo_description)

    @api.constrains('state_marketing', 'website_published')
    def check_state_published(self):
        for rec in self:
            if rec.state_marketing in ('D', 'H'):
                if rec.website_published:
                    rec.website_published = False


class LightingProductFamily(models.Model):
    _inherit = 'lighting.product.family'

    seo_title = fields.Char(string='Meta title', translate=True)
    seo_url = fields.Char(string='URL')
    seo_description = fields.Text(string='Meta description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword',
                                       relation='lighting_product_family_seo_keyword_rel',
                                       column1='family_id', column2='keyword_id', string='Keywords')

    meta_title_length = fields.Integer(string='Meta title length', compute='_compute_lengths', readonly=True)
    meta_description_length = fields.Integer(string='Meta description length', compute='_compute_lengths',
                                             readonly=True)

    @api.depends('seo_title', 'seo_description')
    def _compute_lengths(self):
        for rec in self:
            if rec.seo_title:
                rec.meta_title_length = len(rec.seo_title)
            if rec.seo_description:
                rec.meta_description_length = len(rec.seo_description)

    meta_preview = fields.Char(string='Preview', compute='_compute_preview', readonly=True)

    @api.depends('seo_title', 'seo_url', 'seo_description')
    def _compute_preview(self):
        for rec in self:
            rec.meta_preview = seo_preview(rec.seo_title, rec.seo_url, rec.seo_description)


class LightingProductCategory(models.Model):
    _inherit = 'lighting.product.category'

    seo_title = fields.Char(string='Meta title', translate=True)
    seo_url = fields.Char(string='URL')
    seo_description = fields.Char(string='Meta description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword',
                                       relation='lighting_product_category_seo_keyword_rel',
                                       column1='category_id', column2='keyword_id', string='Keywords')

    meta_title_length = fields.Integer(string='Meta title length', compute='_compute_lengths', readonly=True)
    meta_description_length = fields.Integer(string='Meta description length', compute='_compute_lengths',
                                             readonly=True)

    @api.depends('seo_title', 'seo_description')
    def _compute_lengths(self):
        for rec in self:
            if rec.seo_title:
                rec.meta_title_length = len(rec.seo_title)
            if rec.seo_description:
                rec.meta_description_length = len(rec.seo_description)

    meta_preview = fields.Char(string='Preview', compute='_compute_preview', readonly=True)

    @api.depends('seo_title', 'seo_url', 'seo_description')
    def _compute_preview(self):
        for rec in self:
            rec.meta_preview = seo_preview(rec.seo_title, rec.seo_url, rec.seo_description)


class LightingProductApplication(models.Model):
    _inherit = 'lighting.product.application'

    seo_title = fields.Char(string='Meta title', translate=True)
    seo_url = fields.Char(string='URL')
    seo_description = fields.Char(string='Meta description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword',
                                       relation='lighting_product_application_seo_keyword_rel',
                                       column1='application_id', column2='keyword_id', string='Keywords')

    meta_title_length = fields.Integer(string='Meta title length', compute='_compute_lengths', readonly=True)
    meta_description_length = fields.Integer(string='Meta description length', compute='_compute_lengths',
                                             readonly=True)

    @api.depends('seo_title', 'seo_description')
    def _compute_lengths(self):
        for rec in self:
            if rec.seo_title:
                rec.meta_title_length = len(rec.seo_title)
            if rec.seo_description:
                rec.meta_description_length = len(rec.seo_description)

    meta_preview = fields.Char(string='Preview', compute='_compute_preview', readonly=True)

    @api.depends('seo_title', 'seo_url', 'seo_description')
    def _compute_preview(self):
        for rec in self:
            rec.meta_preview = seo_preview(rec.seo_title, rec.seo_url, rec.seo_description)


class LightingCatalog(models.Model):
    _inherit = 'lighting.catalog'

    seo_title = fields.Char(string='Meta title', translate=True)
    seo_url = fields.Char(string='URL')
    seo_description = fields.Char(string='Meta description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword',
                                       relation='lighting_catalog_seo_keyword_rel',
                                       column1='catalog_id', column2='keyword_id', string='Keywords')
    meta_title_length = fields.Integer(string='Meta title length', compute='_compute_lengths', readonly=True)
    meta_description_length = fields.Integer(string='Meta description length', compute='_compute_lengths',
                                             readonly=True)

    @api.depends('seo_title', 'seo_description')
    def _compute_lengths(self):
        for rec in self:
            if rec.seo_title:
                rec.meta_title_length = len(rec.seo_title)
            if rec.seo_description:
                rec.meta_description_length = len(rec.seo_description)

    meta_preview = fields.Char(string='Preview', compute='_compute_preview', readonly=True)

    @api.depends('seo_title', 'seo_url', 'seo_description')
    def _compute_preview(self):
        for rec in self:
            rec.meta_preview = seo_preview(rec.seo_title, rec.seo_url, rec.seo_description)
