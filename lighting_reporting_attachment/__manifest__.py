# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Lighting Reporting Attachment",
    'description': """* Enables the option to use a selected attachments as a product datasheet""",
    'version': '11.0.1.0.1',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'depends': [
        'lighting_reporting',
    ],
    'data': [
        'views/product_attachment_views.xml',
    ],
    'installable': True,
}
