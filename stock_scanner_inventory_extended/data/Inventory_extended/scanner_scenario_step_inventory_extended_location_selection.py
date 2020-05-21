# flake8: noqa
# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer

t.set_tmp_value('quantity', float(m))

product = model.browse(t.get_tmp_value('product_id'))

act = 'T'
res = [
    _('Product : [%s] %s') % (product.default_code, product.name),
    _('Quantity : %g %s') % (float(m), product.uom_id.name),
    '',
    _('Location ?'),
]
