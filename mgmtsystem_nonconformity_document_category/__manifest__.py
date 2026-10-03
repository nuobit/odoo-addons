# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Management System Nonconformity Document Category",
    "summary": "Offer the documents of classified categories as nonconformity "
    "procedures",
    "version": "14.0.1.0.0",
    "category": "Management System",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "document_page_procedure",
        "mgmtsystem_document_category",
        "mgmtsystem_nonconformity",
    ],
    "data": [
        "data/document_page_data.xml",
        "views/mgmtsystem_nonconformity.xml",
    ],
    "auto_install": True,
}
