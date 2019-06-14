# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Sage-Odoo connector Snapshot",
    'version': '11.0.0.2.0',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Connector',
    'website': 'https://www.nuobit.com',
    'depends': [
        'connector_sage',
    ],
    'external_dependencies': {
        'python': [
            'sqlite3',
        ],
    },
    'data': [
        'security/database.xml',
        'security/ir.model.access.csv',
        'views/database_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
}
