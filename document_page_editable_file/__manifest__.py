# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Document Page Editable File",
    "summary": "Keep the editable files of each version of a document, "
    "visible to the Knowledge editors only.",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "category": "Knowledge Management",
    "depends": [
        "document_page",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/document_page_editable_file_security.xml",
        "views/document_page_editable_file_views.xml",
        "views/document_page_history_views.xml",
        "views/document_page_views.xml",
    ],
}
