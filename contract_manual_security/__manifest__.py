# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Contract Manual Security",
    "summary": "This module conditionally displays the 'Create invoices' "
    "button within contracts based on a permission",
    "version": "14.0.1.0.0",
    "category": "Contract Management",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "contract",
    ],
    "data": [
        "security/contract_security.xml",
        "views/contract_views.xml",
    ],
}
