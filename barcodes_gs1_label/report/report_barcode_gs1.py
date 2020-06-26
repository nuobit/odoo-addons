# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, _
from odoo.exceptions import UserError


def chunks(li, n, padding=False):
    if not li:
        return
    sub_li = li[:n]
    if padding:
        diff = n - len(sub_li)
        if diff:
            sub_li += [None] * diff
    yield sub_li
    yield from chunks(li[n:], n, padding=padding)


class ReportGS1Barcode(models.AbstractModel):
    _name = 'report.barcodes_gs1_label.report_gs1_barcode'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data:
            raise UserError(_("Expected data to be passed to the report"))

        model = data['model']
        docids = data['ids']

        barcode_type = data['barcode_type']
        with_stock = data['with_stock']

        cols = data['layout']['cols']
        start_cell = data['layout']['start_cell']
        labels_page_count = data['layout']['labels_page_count']
        label_copies = data['layout']['label_copies']

        docs1 = []
        if model == 'product.product':
            for doc in self.env[model].browse(docids).sorted(lambda x: x.default_code):
                quants = self.env['stock.quant']
                if with_stock:
                    quants = self.env['stock.quant'].search([
                        ('product_id', '=', doc.id),
                        ('location_id.usage', '=', 'internal'),
                        ('quantity', '>', 0),
                    ])

                if doc.tracking == 'none':
                    if not with_stock or quants:
                        docs1.append({
                            'name': doc.name,
                            'tracking': doc.tracking,
                            'barcode': doc.barcode,
                            'default_code': doc.default_code,
                        })
                elif doc.tracking in ('lot', 'serial'):
                    if not with_stock:
                        lots = self.env['stock.production.lot'].search([
                            ('product_id', '=', doc.id)])
                    else:
                        lots = quants.mapped('lot_id')

                    for l in lots.sorted(lambda x: x.name):
                        docs1.append({
                            'name': doc.name,
                            'tracking': doc.tracking,
                            'barcode': doc.barcode,
                            'tracking_code': l.name,
                            'default_code': doc.default_code,
                        })
        elif model == 'stock.production.lot':
            for doc in self.env[model].browse(docids) \
                    .filtered(lambda x: x.product_id.tracking in ('lot', 'serial')) \
                    .sorted(lambda x: x.product_id.default_code):
                quants_count = 0
                if with_stock:
                    quants_count = bool(self.env['stock.quant'].search_count([
                        ('product_id', '=', doc.product_id.id),
                        ('location_id.usage', '=', 'internal'),
                        ('lot_id', '=', doc.id),
                        ('quantity', '>', 0),
                    ]))

                if not with_stock or quants_count:
                    docs1.append({
                        'name': doc.product_id.name,
                        'tracking': doc.product_id.tracking,
                        'barcode': doc.product_id.barcode,
                        'tracking_code': doc.name,
                        'default_code': doc.product_id.default_code,
                    })
        else:
            raise UserError(_("Unexpected model '%s'") % model)

        docs = []
        for doc in docs1:
            gas1_barcode = {}
            if doc['barcode']:
                gas1_barcode['01'] = doc['barcode']
            if doc['tracking'] == 'lot':
                gas1_barcode['10'] = doc['tracking_code']
            elif doc['tracking'] == 'serial':
                gas1_barcode['21'] = doc['tracking_code']
            doc['barcode_values'] = gas1_barcode

            barcode_string_l = []
            for ai, value in gas1_barcode.items():
                if ai == '01':
                    gtin = value.rjust(14, '0')
                    barcode_string_l.append(ai + gtin)
                else:
                    barcode_string_l.append(ai + value)
            doc['barcode_string'] = r'\F' + ''.join(barcode_string_l)

            if doc['tracking'] in ('none', 'lot') and label_copies > 1:
                docs += [doc] * label_copies
            else:
                docs.append(doc)

        docs_padded = [None] * (start_cell - 1) + docs

        docs_paginated = chunks(docs_padded, labels_page_count)

        docs_page_rows = [list(chunks(x, cols, padding=True)) for x in docs_paginated]

        return {
            'docs': docs_page_rows,
            'barcode_type': barcode_type,
            'layout': data['layout'],
        }
