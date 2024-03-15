# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Contract Mandate Default",
    "summary": "This module always assigns the valid mandate "
    "of the partner in the contract.",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": ["contract_mandate"],
    "category": "Sales Management",
    "post_init_hook": "post_init_hook",
    "license": "AGPL-3",
    "data": ["views/contract_view.xml"],
}
