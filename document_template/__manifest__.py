{
    "name": "Document Template",
    "summary": "Standalone module for managing document templates and their files.",
    "version": "16.0.1.0.1",
    "category": "Documents",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/document_template_views.xml",
        "views/document_template_menu.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
