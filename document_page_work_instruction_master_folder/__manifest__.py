# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dev1@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Document Page Work Instruction Master Folder",
    "summary": "Work instructions menu on the master folders of each company",
    "version": "14.0.1.0.0",
    "category": "Management System",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": ["document_page_work_instruction", "mgmtsystem_document_master_folder"],
    "data": [
        "data/document_page_data.xml",
        "views/document_page_actions.xml",
    ],
    "auto_install": True,
}
