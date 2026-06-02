# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dev1@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Management System Document Category",
    "summary": "Classify document categories by management system type so the "
    "nonconformity procedure field stops depending on category names",
    "version": "14.0.1.0.0",
    "category": "Management System",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "document_page",
        "mgmtsystem_nonconformity",
    ],
    "data": [
        "views/document_page.xml",
        "views/mgmtsystem_nonconformity.xml",
    ],
}
