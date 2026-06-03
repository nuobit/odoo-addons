# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dev1@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Management System Audit Document Category",
    "summary": "Filter audit verification procedures by document category type "
    "instead of by category name",
    "version": "14.0.1.0.0",
    "category": "Management System",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "mgmtsystem_audit",
        "mgmtsystem_document_category",
    ],
    "data": [
        "views/mgmtsystem_audit.xml",
    ],
}
