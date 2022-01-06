# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "FacturaE service info",
    "summary": "This module propagates the service info of the "
    "sale order to the invoice line facturae data.",
    "version": "11.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_facturae",
        "sale_order_service",
    ],
    "data": [],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["eantones"],
}
