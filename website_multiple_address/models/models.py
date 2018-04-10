from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_company_address = fields.Boolean(compute="_compute_is_company_address")

    show_address_website = fields.Boolean(string="Show address on website")
    address_website_sequence = fields.Integer(string="Address website sequence", default=1)
    show_map_website = fields.Boolean(string="Show map on website")

    def _compute_is_company_address(self):
        for rec in self:
            rec.is_company_address = self.env['res.company'].search_count(
                [('partner_id', '=', rec.parent_id.id or rec.id)]) != 0


class Company(models.Model):
    _inherit = 'res.company'

    address_partner_ids = fields.One2many(comodel_name='res.partner', compute="_compute_address_partner_ids")

    @api.depends('partner_id.show_address_website', 'partner_id.child_ids.show_address_website')
    def _compute_address_partner_ids(self):
        for rec in self:
            rec.address_partner_ids = (
                    rec.partner_id | rec.partner_id.child_ids).filtered(
                lambda x: x.show_address_website).sorted(
                lambda x: x.address_website_sequence)

    @api.multi
    def google_map_img_partner(self, partner, zoom=8, width=298, height=298):
        return partner and partner.google_map_img(zoom, width, height) or None

    @api.multi
    def google_map_link_partner(self, partner, zoom=8):
        return partner and partner.google_map_link(zoom) or None
