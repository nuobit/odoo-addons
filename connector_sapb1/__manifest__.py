# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Connector SAP B1",
    'description': "SAP Business One connector",
    'version': '11.0.0.1.2',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Connector',
    'website': 'https://github.com/nuobit',
    'external_dependencies': {
        'python': [
            'paramiko',
            'hdbcli',
        ],
    },
    'depends': [
        'connector',
    ],
    'data': [
        'views/backend_views.xml',
        'views/menus.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
