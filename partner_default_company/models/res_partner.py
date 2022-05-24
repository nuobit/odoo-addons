# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    def _default_company(self):
        return self.env.company.id

    company_id = fields.Many2one(default=_default_company)
