# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_batch_sending_method = fields.Selection(
        selection_add=[("emailattachments", "e-mail (Attach documents)")],
        ondelete={"emailattachments": "set default"},
    )
