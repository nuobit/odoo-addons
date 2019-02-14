# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Sage Payroll",
    'version': '11.0.0.8.0',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'website': 'https://www.nuobit.com',
    'depends': [
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/labour_agreement_view.xml',
        'views/payslip_view.xml',
        'views/wage_tag_view.xml',

        'views/menu.xml',
        ],
    'installable': True,
}
