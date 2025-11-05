# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Bijaya Kumal <bkumal@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Quality partner",
    "summary": "This module adds the logic to classify "
    "and evaluate the partner performance",
    "version": "18.0.1.0.0",
    "category": "Website",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": ["purchase"],
    "data": [
        "security/quality_partner_security.xml",
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/quality_partner_menu_views.xml",
        "views/quality_partner_classification_views.xml",
        "views/quality_partner_document_type_views.xml",
        "views/quality_partner_document_views.xml",
    ],
}
