# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Sale Report product Type",
    "summary": "This module adds a product_type field to "
    "'Sales -> Reporting -> Sale' in order to "
    "be able to filter and group for this field.",
    "version": "12.0.1.0.1",
    "category": "Reporting",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/OCA/pms",
    "license": "AGPL-3",
    "depends": [
        "sale",
    ],
    "data": [
        "views/sale_report_views.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["eantones"],
}
