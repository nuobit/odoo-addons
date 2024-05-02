# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Maintenance Request Date Editable",
    "summary": "This module allows to edit the date of a maintenance request"
    " if the company parameter is set.",
    "version": "14.0.1.0.0",
    "category": "Manufacturing/Maintenance",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": ["base_maintenance_config", "maintenance"],
    "data": [
        "views/res_config_settings.xml",
        "views/maintenance_views.xml",
    ],
}
