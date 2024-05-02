# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models

from odoo.addons.base.models.res_config import ResConfigModuleInstallationMixin


class ResConfigSettings(models.TransientModel, ResConfigModuleInstallationMixin):
    _inherit = "res.config.settings"

    maintenance_request_date_editable = fields.Boolean(
        related="company_id.maintenance_request_date_editable", readonly=False
    )
