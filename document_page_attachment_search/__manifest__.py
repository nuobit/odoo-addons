# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Document Page Attachment Search",
    "summary": "Extend the document page content search to also match the "
    "indexed text of the files attached to the page (PDF, docx, xlsx, "
    "OpenDocument, etc.).",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "category": "Knowledge Management",
    "depends": [
        "document_page",
        "attachment_indexation",
    ],
    "data": [
        "views/document_page_views.xml",
    ],
    "external_dependencies": {"python": ["pdfminer.six"]},
    "installable": True,
}
