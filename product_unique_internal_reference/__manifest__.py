# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Product unique internal reference',
    'summary': 'This module ensures that you enter a Unique Internal Reference (default_code) for your Products',
    'version': '11.0.0.2.0',
    'category': 'Sales',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://www.nuobit.com',
    'license': 'AGPL-3',
    'depends': [
        'product',
    ],
    'pre_init_hook': 'pre_init_hook_internal_reference_check',
    'installable': True,
    'auto_install': False,
}
