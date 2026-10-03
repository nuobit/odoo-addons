# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Document Page Distribution Download Log",
    "summary": "Logs who downloads which file of each document page version.",
    "version": "14.0.1.0.0",
    "category": "Knowledge Management",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "document_page_distribution",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/document_page_distribution_download_log_security.xml",
        "views/document_page_history_recipient_download_views.xml",
        "views/document_page_history_views.xml",
        "views/document_page_views.xml",
    ],
}
