# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "POS restaurant line note receipt",
    "version": "12.0.1.0.2",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Point of Sale",
    "website": "https://github.com/nuobit",
    "summary": "This module shows the line note on the receipt on screen and printer.",
    "depends": [
        "pos_restaurant",
    ],
    "data": [
        "views/templates.xml",
    ],
    "qweb": [
        "static/src/xml/pos.xml",
    ],
    "installable": True,
}
