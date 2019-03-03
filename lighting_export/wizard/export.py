# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError



class LightingExport(models.TransientModel):
    _name = "lighting.export"
    _description = "Export data"

    template_id = fields.Many2one(comodel_name='lighting.export.template', ondelete='cascade',
                                  string='Template', required=True)

    interval = fields.Selection(selection=[('all', _('All')), ('selection', _('Selection'))], default='selection')

    hide_empty_fields = fields.Boolean(string="Hide empty fields", default=True)

    lang_id = fields.Many2one(comodel_name='res.lang', required=True)

    output_type = fields.Selection(selection=[], string="Output type", required=True)

    @api.multi
    def export_product(self):
        self.ensure_one()

        return getattr(self, self.output_type)()

