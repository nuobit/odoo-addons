# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Project legal management',
    'summary': 'This module adds the necessary fields to work with '
               'the legal management in the project module',
    'version': '11.0.0.2.1',
    'category': 'Sales',
    'author': 'NuoBiT Solutions, S.L., Kilian Niubo',
    'website': 'https://github.com/nuobit',
    'license': 'AGPL-3',
    'depends': [
        'project',
        'hr',
    ],
    'data': [
        'views/project_views.xml',
        'views/lm_issue_views.xml',
        'views/lm_probability_views.xml',
        'views/lm_resolution_views.xml',
        'views/project_tree.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}
