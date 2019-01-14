# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Sage-Odoo connector",
    'version': '11.0.0.2.1',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Connector',
    'website': 'https://www.nuobit.com',
    'depends': [
        'connector',
        'hr',
        'payroll_sage',
    ],
    'external_dependencies': {
        'python': [
            'pymssql',
        ],
    },
    'data': [
        # 'data/cron.xml',
        'views/sage_backend_view.xml',
        'views/hr_employee_view.xml',
        'views/res_partner_view.xml',
        'views/payroll_sage_labour_agreement_view.xml',
        'views/connector_sage_menu.xml',
        'security/connector_sage.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
