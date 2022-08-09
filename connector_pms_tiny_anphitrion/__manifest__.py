# Copyright NuoBiT Solutions SL (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Connector PMS Tiny",
    "summary": "This module connects with PMS Tiny system and synchronizes reservations",
    "version": "16.0.1.0.0",
    "category": "Connector",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [
            "pymssql",
        ],
    },
    "depends": [
        "connector_extension_mssql",
        "pms_tiny",
    ],
    "data": [
        "security/anphitrion_security.xml",
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "data/queue_data.xml",
        "data/queue_job_function_data.xml",
        "views/pms_tiny_reservation_view.xml",
        "views/pms_tiny_reservation_room_view.xml",
        "views/anphitrion_backend_view.xml",
        "views/anphitrion_reservation_view.xml",
        "views/anphitrion_reservation_room_view.xml",
        "views/anphitrion_menu.xml",
    ],
}
