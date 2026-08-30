# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Document Page Distribution Download Log",
    "summary": "Per-recipient download evidence log for distributed document "
    "page versions.",
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
        "views/document_page_history_recipient_views.xml",
    ],
}
