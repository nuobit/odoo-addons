# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Base User Update Partner",
    "summary": "This module allows modifying the contact related to Users. To do so, "
    "you must belong to the 'Change user related partner' group created in Technical "
    "Settings",
    "version": "16.0.0.0.0",
    "category": "Hidden",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "base",
    ],
    "data": [
        "security/res_groups_security.xml",
        "views/res_users_views.xml",
    ],
}
