# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Document Page Archive Reason",
    "summary": "Require a mandatory reason when archiving document pages; "
    "reason logged in chatter for traceability.",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "category": "Knowledge Management",
    "depends": [
        "document_page",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/document_page_archive_reason.xml",
    ],
}
