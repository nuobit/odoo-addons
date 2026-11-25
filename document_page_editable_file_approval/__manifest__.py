# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Document Page Editable File Approval",
    "summary": "The editable files of a document follow its change requests.",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "category": "Knowledge Management",
    "depends": [
        "document_page_editable_file",
        "document_page_approval",
    ],
    "data": [
        "security/document_page_editable_file_approval_security.xml",
    ],
    "auto_install": True,
    "uninstall_hook": "uninstall_hook",
}
