# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Product unique barcode',
    'summary': 'This module ensures that you enter a Unique Barcode for your Products',
    'version': '11.0.0.1.0',
    'category': 'Sales',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://www.nuobit.com',
    'license': 'AGPL-3',
    'depends': [
        'product_variant_company_aware',
    ],
    'pre_init_hook': 'pre_init_hook_barcode_check',
    'installable': True,
    'auto_install': False,
}
