# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Putaway strategy no internal",
    "summary": "Allow to exclude putaway strategies "
    "if they are applied on an internal operations",
    "version": "14.0.1.0.0",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "stock",
    ],
    "data": [
        "views/product_strategy_views.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["eantones"],
}
