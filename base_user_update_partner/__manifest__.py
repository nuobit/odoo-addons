# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Base User Update Partner",
    "summary": "This module allows modifying the contact related to Users. To do so, "
    "you must belong to the 'Change user related partner' group created in Technical "
    "Settings",
    "version": "14.0.1.0.0",
    "category": "Hidden",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "base",
    ],
    "data": [
        "security/res_groups_security.xml",
        "views/res_users_views.xml",
    ],
}
