# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Translation auto",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Tools",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "base",
    ],
    "data": [
        "views/ir_translation_views.xml",
    ],
    "external_dependencies": {
        "python": [
            "googletrans",
        ],
    },
}
