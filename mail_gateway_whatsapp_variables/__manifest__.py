# Copyright 2025 NuoBiT - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Mail Gateway WhatsApp Variables",
    "version": "16.0.1.0.0",
    "category": "Discuss",
    "summary": "Add variables and buttons support to WhatsApp templates",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "mail_gateway_whatsapp",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/mail_whatsapp_template_variable_views.xml",
        "views/mail_whatsapp_template_views.xml",
    ],
}
