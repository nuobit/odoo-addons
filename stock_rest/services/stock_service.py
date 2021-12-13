# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class StockService(AbstractComponent):
    _name = "stock.service"
    _collection = "stock.rest.services"
    _inherit = "base.rest.service"

    def _get_current_user(self):
        user = self.env["res.users"].search(
            [
                ("id", "=", self.env.uid),
            ]
        )
        if not user:
            raise IOError("No user found with current id")
        elif len(user) > 1:
            raise IOError("Detected more than one user with the same id")
        return user

    def _get_current_company(self):
        company = self.env.user.company_id
        if not company:
            raise IOError("Cannot get the company from the user")
        return company
