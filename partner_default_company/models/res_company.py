# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class Company(models.Model):
    _inherit = "res.company"

    @api.model
    def create(self, vals):
        return super(Company, self.with_context(company_creation=True)).create(vals)
