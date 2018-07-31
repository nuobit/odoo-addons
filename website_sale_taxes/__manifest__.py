# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Website Sale Taxes",
    "description": "This module extends the functionality of website_sale addding" 
                   "selected taxes in:"
                   " * Shopping cart lines at checkout and cart"
                   " * Product detail ",
    "version": "10.0.0.1.0",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "E-commerce",
    "website": "https://www.nuobit.com",
    "depends": ["website_sale"],
    "data": [
        "views/website_sale_templates.xml",
        ],
    "installable": True,
}