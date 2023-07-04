# Copyright NuoBiT Solutions SL (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "PMS Tiny Astrochannel",
    "summary": "This module emulates an Astrochannel API to be accessed by Astro",
    "version": "16.0.1.0.0",
    "category": "API",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "pms_tiny",
    ],
    "data": [
        "security/pms_tiny_astrochannel_security.xml",
        "security/ir.model.access.csv",
        "views/pms_tiny_astrochannel_log_view.xml",
        "views/pms_tiny_astrochannel_service_view.xml",
        "views/pms_tiny_astrochannel_menu.xml",
        "views/pms_tiny_reservation_view.xml",
        "views/pms_tiny_reservation_room_view.xml",
    ],
}
