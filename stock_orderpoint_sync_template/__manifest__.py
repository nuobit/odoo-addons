# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Stock orderpoint sync template",
    'summary': "Allows create reordering rules for multiple products and different "
               "parameters per product in one go and keep them synchronized with "
               "the base template",
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'category': 'Warehouse',
    'version': '11.0.0.1.0',
    'license': 'AGPL-3',
    'website': 'https://github.com/nuobit',
    'depends': [
        'stock',
    ],
    'data': [
        'views/orderpoint_views.xml',
        'views/orderpoint_sync_template_views.xml',
        "security/orderpoint_sync_template_security.xml",
        "security/ir.model.access.csv",
    ],
    'installable': True,
}
