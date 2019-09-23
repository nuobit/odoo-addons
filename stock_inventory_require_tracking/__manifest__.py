# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Stock inventory require tracking",
    'summary': "If a product has tracking defined, it does not allow to validate "
               "inventory lines without a tracking number (Lot/Serial)",
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'category': 'Warehouse',
    'version': '11.0.0.1.0',
    'license': 'AGPL-3',
    'website': 'https://github.com/nuobit',
    'depends': [
        'stock',
    ],
    'data': [
    ],
    'installable': True,
}
