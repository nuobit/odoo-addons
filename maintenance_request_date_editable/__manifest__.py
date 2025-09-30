# Copyright NuoBiT Solutions SL - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Maintenance Request Date Editable",
    "summary": "This module allows to edit the date of a maintenance request"
    " if the company parameter is set.",
    "version": "18.0.1.0.0",
    "category": "Manufacturing/Maintenance",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": ["maintenance"],
    "data": [
        "views/res_config_settings.xml",
        "views/maintenance_views.xml",
    ],
}
