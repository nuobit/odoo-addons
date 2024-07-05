# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class Http(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        return super(
            Http, self.with_context(session_info_check_internal_users=True)
        ).session_info()
