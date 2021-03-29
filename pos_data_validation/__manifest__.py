# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "POS data validation",
    "version": "12.0.1.0.1",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Point of Sale",
    "website": "https://github.com/OCA/pms",
    "summary": "This modules makes validations to minimize the effect of "
    "the backend ignoring the propagation of errors",
    "depends": [
        "point_of_sale",
    ],
    "data": [
        "views/templates.xml",
    ],
    "installable": True,
}
