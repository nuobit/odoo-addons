# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Document Page Distribution",
    "summary": "Distribute the current version of a document page to the users "
    "with read access and keep an auditable per-recipient distribution log.",
    "version": "14.0.1.0.0",
    "category": "Knowledge Management",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "document_page",
        "document_page_access_group",
        "mail",
    ],
    "data": [
        "security/document_page_distribution_security.xml",
        "security/ir.model.access.csv",
        "data/mail_template_data.xml",
        "wizards/document_page_distribute_views.xml",
        "views/document_page_history_recipient_views.xml",
        "views/document_page_history_views.xml",
        "views/document_page_views.xml",
        "views/res_config_settings_views.xml",
    ],
}
