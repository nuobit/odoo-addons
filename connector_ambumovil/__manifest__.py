# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Odoo-Ambumovil connector",
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'category': 'Connector',
    'version': '11.0.0.1.5',
    'license': 'AGPL-3',
    'website': 'https://github.com/nuobit',
    'depends': [
        'stock',
        'stock_picking_employee',
        'stock_picking_partner_ref',
        'stock_picking_partner',
        'stock_location_code',
        'connector_sage',
    ],
    'data': [
    ],
    'installable': True,
}
