# flake8: noqa
# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer

from odoo import fields

# No current inventory, create a new one
if not t.get_tmp_value('inventory_id'):
    stock_inventory = env['stock.inventory'].create({
        'name': '%s : %s' % (t.code, fields.Datetime.now()),
    })
    t.set_tmp_value('inventory_id', stock_inventory.id)
elif tracer == 'location' and t.get_tmp_value('product_id'):
    stock_inventory_id = t.get_tmp_value('inventory_id')

    product = model.browse(t.get_tmp_value('product_id'))

    quantity = t.get_tmp_value('quantity')

    location = env['stock.location'].search([
        '|', '&', ('barcode', '!=', False), ('barcode', '=', m),
        '&', ('barcode', '=', False), ('name', '=', m),
    ])

    env['stock.inventory.line'].create({
        'inventory_id': stock_inventory_id,
        'product_id': product.id,
        'product_uom_id': product.uom_id.id,
        'product_qty': quantity,
        'location_id': location.id,
    })
    t.set_tmp_value('product_id', None)
    t.set_tmp_value('quantity', None)

act = 'T'
res = [
    _('Product code ?'),
]
