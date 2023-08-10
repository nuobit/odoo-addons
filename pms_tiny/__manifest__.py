# Copyright NuoBiT Solutions SL (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "PMS Tiny",
    "summary": "A really simple PMS system",
    "version": "16.0.1.0.0",
    "category": "PMS",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": ["mail"],
    "data": [
        "security/pms_tiny_security.xml",
        "security/ir.model.access.csv",
        "views/pms_tiny_property_view.xml",
        "views/pms_tiny_reservation_view.xml",
        "views/pms_tiny_reservation_room_view.xml",
        "views/pms_tiny_menu.xml",
    ],
}