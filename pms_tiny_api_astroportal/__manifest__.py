# Copyright NuoBiT Solutions SL (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "PMS Tiny API Astroportal",
    "summary": "This module enables an API to be accessed by Astroportales",
    "version": "16.0.1.0.0",
    "category": "API",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "pms_tiny",
    ],
    "data": [
        "security/pms_tiny_api_astroportal_security.xml",
        "security/ir.model.access.csv",
        "views/pms_tiny_api_astroportal_view.xml",
        "views/pms_tiny_api_astroportal_menu.xml",
        "views/pms_tiny_reservation_view.xml",
    ],
}
