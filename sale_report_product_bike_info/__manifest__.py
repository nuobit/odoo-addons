# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Sale Report product bike data",
    "summary": "This module adds all the fields in the 'Bike Data' tab "
    "to 'Sales -> Reporting -> Sale' in order to be able to "
    "filter and group for these fields.",
    "version": "14.0.1.0.0",
    "category": "Reporting",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "sale",
        "product_bike_info",
    ],
    "data": [
        "views/sale_report_views.xml",
    ],
    "auto_install": True,
    "development_status": "Beta",
    "maintainers": ["eantones"],
}
