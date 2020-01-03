# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Invoice batches",
    'version': '11.0.1.0.3',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Accounting',
    'website': 'https://github.com/nuobit',
    'depends': [
        'sale',
        'l10n_es_facturae',
        'account_invoice_report_service',
    ],
    'data': [
        'security/account_invoice_batch.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'wizard/account_invoice_batch_process.xml',
        'wizard/sale_make_invoice_advance_views.xml',
        'views/res_partner.xml',
        'views/account_invoice.xml',
        'views/account_invoice_batch.xml',
        'views/menu.xml',
    ],
    'installable': True,
}
