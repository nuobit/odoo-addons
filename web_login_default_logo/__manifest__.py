# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Web login default logo",
    "summary": "This module forces default Odoo logo at login screen.",
    "version": "14.0.1.0.0",
    "category": "Web",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "web",
    ],
    "data": [
        "views/webclient_templates.xml",
    ],
    "installable": True,
    "auto_install": False,
}
