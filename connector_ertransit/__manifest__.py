# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Connector ERTransit / Erhardt",
    'description': "ERTransit / Erhardt connector",
    'version': '11.0.0.1.5',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Connector',
    'website': 'https://github.com/nuobit',
    'external_dependencies': {
        'python': [
            'requests',
            'lxml',
        ],
    },
    'depends': [
        'connector',
    ],
    'data': [
        'views/backend_views.xml',
        'views/menus.xml',
        'templates/ertransit_template.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
