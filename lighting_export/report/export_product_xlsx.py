# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, models
from odoo.exceptions import UserError, ValidationError


class ExportProductXlsx(models.AbstractModel):
    _name = 'report.lighting_export.export_product_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        template_id = self.env['lighting.export.template'].browse(objects[0].id)

        objects = objects[1:]

        bold = workbook.add_format({'bold': True})

        fields = objects.fields_get([x.field_id.name for x in template_id.line_ids])

        headers = []
        for line in template_id.line_ids.sorted(lambda x: x.sequence):
            item = objects.fields_get([line.field_id.name])
            if item:
                headers.append(tuple(item.items())[0])

        sheet = workbook.add_worksheet('test')
        row = col = 0

        xlsx_header = [meta['string'] for _, meta in headers]
        for col_header in xlsx_header:
            sheet.write(row, col, col_header, bold)
            col += 1

        row = 1
        for obj in objects:
            col = 0
            for field, meta in headers:
                datum = getattr(obj, field)
                if datum:
                    if meta['type'] == 'selection':
                        datum = dict(meta['selection']).get(datum)
                    elif meta['type'] == 'many2many':
                        datum = ','.join([x.display_name for x in datum])
                    elif meta['type'] == 'many2one':
                        datum = datum.display_name
                    elif meta['type'] == 'one2many':
                        if field in ('dimension_ids', 'recess_dimension_ids',
                                     'auxiliary_equipment_model_ids', 'fan_wattage_ids'):
                            datum = datum.export_name()
                        else:
                            datum = 'NOT SUPPORTED'

                    sheet.write(row, col, datum)
                col += 1
            row += 1

        """
        def fill_table(sheet_name, lines, received_lines=False):
            sheet = workbook.add_worksheet(sheet_name[:31])
            row = col = 0
            xlsx_header = [
                _('Invoice'),
                _('Date'),
                _('Partner'),
                _('VAT'),
                _('Base'),
                _('Tax'),
                _('Fee'),
                _('Total'),
            ]
            if received_lines:
                xlsx_header.insert(0, _('Reference'))
            for col_header in xlsx_header:
                sheet.write(row, col, col_header, bold)
                col += 1

            row = 1
            for line in lines:
                for tax_line in line.tax_line_ids:
                    col = 0
                    if received_lines:
                        sheet.write(row, col, line.invoice_id.reference)
                        col += 1
                    sheet.write(row, col, line.invoice_id.number)
                    col += 1
                    sheet.write(row, col, line.invoice_date)
                    col += 1
                    sheet.write(row, col, line.partner_id.name)
                    col += 1
                    sheet.write(row, col, line.vat_number)
                    col += 1
                    sheet.write(row, col, tax_line.base_amount)
                    col += 1
                    sheet.write(row, col, tax_line.tax_id.name)
                    col += 1
                    sheet.write(row, col, tax_line.tax_amount)
                    col += 1
                    sheet.write(row, col, tax_line.total_amount)
                    row += 1

        if book.issued_line_ids:
            report_name = _('Issued Invoices')
            lines = book.issued_line_ids
            fill_table(report_name, lines)
        if book.rectification_issued_line_ids:
            report_name = _('Issued Refund Invoices')
            lines = book.rectification_issued_line_ids
            fill_table(report_name, lines)
        if book.received_line_ids:
            report_name = _('Received Invoices')
            lines = book.received_line_ids
            fill_table(report_name, lines, received_lines=True)
        if book.rectification_received_line_ids:
            report_name = _('Received Refund Invoices')
            lines = book.rectification_received_line_ids
            fill_table(report_name, lines, received_lines=True)
    """