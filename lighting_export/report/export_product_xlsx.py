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

        headers = []
        for line in template_id.line_ids.sorted(lambda x: x.sequence):
            item = objects.fields_get([line.field_id.name])
            if item:
                field, meta = tuple(item.items())[0]
                if line.label and line.label.strip():
                    meta['string'] = line.label
                headers.append((field, meta))

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