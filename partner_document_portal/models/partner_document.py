# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PartnerDocument(models.Model):
    _name = "partner.document"
    _inherit = ["partner.document", "portal.mixin"]
