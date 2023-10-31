# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Partner Document",
    "summary": "This module adds the logic to classify and evaluate the partner performance",
    "version": "16.0.1.0.2",
    "category": "Website",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": ["contacts"],
    "data": [
        "security/partner_documents_security.xml",
        "security/ir.model.access.csv",
        "views/partner_document_menu_views.xml",
        "views/res_partner_views.xml",
        "views/partner_classification_views.xml",
        "views/partner_document_type_views.xml",
        "views/partner_document_views.xml",
        "wizard/partner_document_expired_wizard.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "partner_document/static/src/js/kanban_res_partner_button.js",
            "partner_document/static/src/js/list_res_partner_button.js",
            "partner_document/static/src/xml/kanban_res_partner_button.xml",
            "partner_document/static/src/xml/list_res_partner_button.xml",
        ],
    },
    "installable": True,
    "auto_install": False,
}