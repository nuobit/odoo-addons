# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Report qweb PDF chunks',
    'summary': 'This module temporarily splits all selected documents to print into chunks '
               'and invokes the external Wkhtmltopdf (0.12.5) program for each chunk to '
               'avoid the well known memory problems when printing many documents.'
               'The fragments are concatenated at the end, returning a single huge PDF file '
               'as the user expects.',
    'version': '11.0.1.0.0',
    'category': 'Reporting',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://github.com/nuobit',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
    ],
    'installable': True,
    'auto_install': False,
}
