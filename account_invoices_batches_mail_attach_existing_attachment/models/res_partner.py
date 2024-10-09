# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_batch_sending_method = fields.Selection(
        selection_add=[("emailattachments", _("e-mail (Attach documents)"))],
        ondelete={"emailattachments": "set default"},
    )
