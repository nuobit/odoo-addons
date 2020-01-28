# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrderEmailImportResult(models.TransientModel):
    _name = "sale.order.email.import.result"

    errors = fields.Text(readonly=True)
