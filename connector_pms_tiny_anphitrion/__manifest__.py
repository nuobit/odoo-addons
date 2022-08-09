# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Connector PMS Tiny",
    "summary": "This module connects with PMS Tiny system and synchronizes reservations",
    "version": "14.0.1.0.0",
    "category": "Connector",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [
            "pymssql",
        ],
    },
    "depends": [
        "connector_extension",
        "pms_tiny",
    ],
    "data": [
        "security/anphitrion_security.xml",
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "data/queue_data.xml",
        "data/queue_job_function_data.xml",
        "views/pms_tiny_reservation_view.xml",
        "views/anphitrion_backend_view.xml",
        "views/anphitrion_reservation_view.xml",
        "views/anphitrion_menu.xml",
    ],
}
