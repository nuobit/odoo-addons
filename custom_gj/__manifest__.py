# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "GJ Customizations",
    'description': "GJ Customizations",
    'version': '11.0.0.1.0',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'depends': ['account', 'web', 'sale', 'partner_fax'],
    'data': [
        'views/templates.xml',
        'views/report_templates.xml',
        'views/res_company_view.xml',
        'views/report_invoice.xml',
        'views/invoice_report_templates.xml',
    ],
    'installable': True,
}
