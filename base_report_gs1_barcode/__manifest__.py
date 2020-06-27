# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Report GS1 barcodes',
    'summary': 'This module adds a GS1-128 and GS1-Datamatrix barcode format support',
    'version': '12.0.1.0.1',
    'category': 'Reporting',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://github.com/nuobit',
    'license': 'AGPL-3',
    'external_dependencies': {
        'python': [
            'pystrich',
        ],
    },
    'depends': [
        'base',
    ],
    'installable': True,
    'development_status': 'Beta',
    'maintainers': ['eantones'],
    'auto_install': False,
}
