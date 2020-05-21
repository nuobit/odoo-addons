# flake8: noqa
# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer

# flake8: noqa
# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer

product = model.search([
    '|', '&', ('barcode', '!=', False), ('barcode', '=', m),
    '&', ('barcode', '=', False), ('default_code', '=', m),
])
t.set_tmp_value('product_id', product.id)

act = 'Q'
res = [
    _('Product : [%s] %s') % (product.default_code, product.name),
    _('UoM : %s') % product.uom_id.name,
    '',
    _('Select quantity'),
]
