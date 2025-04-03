# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.portal.controllers.portal import CustomerPortal

CustomerPortal.MANDATORY_BILLING_FIELDS.extend(["mobile"])
