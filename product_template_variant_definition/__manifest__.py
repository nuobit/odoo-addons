# Copyright 2024 NuoBiT Solutions S.L. - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Product Template Duplicate No Attributes",
    "summary": "Change the way Odoo identifies if a template "
    "has or not has variants. Not counting the "
    "product.product but using the attributes "
    "defined instead.",
    "version": "14.0.1.0.0",
    "category": "Product Management",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": ["product"],
    "data": [
        "views/product_template_views.xml",
    ],
}
