# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Document Page Editable File",
    "summary": "Keep the editable file (Word) of a document next to its PDF, "
    "visible to a restricted group only, with the history of its versions.",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "category": "Knowledge Management",
    "depends": [
        "document_page",
        "document_page_access_group",
    ],
    "data": [
        "security/security.xml",
        "views/document_page_history_views.xml",
        "views/document_page_views.xml",
    ],
}
