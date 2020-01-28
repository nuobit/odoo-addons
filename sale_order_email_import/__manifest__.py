# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Sale order email import",
    'summary': "Get emails from a remote folder and register them.",
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'category': 'Sales',
    'version': '11.0.1.1.9',
    'license': 'AGPL-3',
    'website': 'https://github.com/nuobit',
    'depends': [
        'sale',
    ],
    'external_dependencies': {
        'python': [
            'smb',
            'extract_msg',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_email_import_result.xml',
        'views/sale_email.xml',
        'views/sale_email_source.xml',
    ],
    'installable': True,
}
