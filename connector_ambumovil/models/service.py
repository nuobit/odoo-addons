# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api


class AmbumovilService(models.AbstractModel):
    _name = "ambumovil.service"

    @api.model
    def get_ambulance_stock(self, code):
        company_id = self.env.user.company_id.id
        quants = self.env['stock.quant'].search([
            ('company_id', '=', company_id),
            ('location_id.code', '=', code),
            ('quantity', '>', 0),
        ])

        product_stock_ld = []
        for q in quants:
            quant_d = {
                'product_id': q.product_id.id,
                'product_name': q.product_id.name,
                'quantity': q.quantity,
            }
            if q.product_id.default_code:
                quant_d.update({
                    'reference': q.product_id.default_code,
                })
            if q.lot_id:
                quant_d.update({
                    'tracking_id': q.lot_id.id,
                    'tracking_type': q.product_id.tracking,
                    'tracking_name': q.lot_id.name,
                })

            product_stock_ld.append(quant_d)

        return product_stock_ld

    @api.model
    def consume_ambulance_stock(self, code, service_num, moves, employees, validate=True):
        company_id = self.env.user.company_id.id

        picking_type_id = self.env['stock.picking.type'].search([
            ('name', '=', 'Internal Transfers'),
        ], order='id asc', limit=1)

        src_location_id = self.env['stock.location'].search([
            ('company_id', '=', company_id),
            ('code', '=', code),
        ])

        dst_location_id = self.env['stock.location'].search([
            ('company_id', '=', company_id),
            ('code', '=', 'CONSUMOSCLIENTE'),
        ])

        ## tractem els movs
        # agrupem per article
        moves9 = {}
        for m in moves:
            product_id = m['product_id']
            if product_id not in moves9:
                moves9[product_id] = []
            moves9[product_id].append(m)

        move_lines = []
        for product_id, pmoves in moves9.items():
            obj = self.env['product.product'].browse(product_id)
            move_lines.append({
                'product_id': obj.id,
                'product_uom': obj.uom_id.id,
                'name': obj.display_name,
                'picking_type_id': picking_type_id.id,
                'origin': False,
            })

        picking_values = {
            'picking_type_id': picking_type_id.id,
            'location_id': src_location_id.id,
            'location_dest_id': dst_location_id.id,
            'partner_ref': service_num,
        }

        if move_lines:
            picking_values.update({
                'move_lines': [(0, False, v) for v in move_lines],
            })

        # empleats
        if employees:
            sage_company_id = self.env['sage.backend'].sudo().search([
                ('company_id', '=', company_id),
            ]).sage_company_id
            employee_ids = self.env['sage.hr.employee'].sudo().search([
                ('company_id', '=', company_id),
                ('sage_codigo_empresa', '=', sage_company_id),
                ('sage_codigo_empleado', 'in', employees),
            ]).mapped('odoo_id.id')
            if employee_ids:
                picking_values.update({
                    'employee_ids': [(6, False, employee_ids)],
                })

        # creem el picking
        picking_id = self.env['stock.picking'].create(picking_values)

        for move_line in picking_id.move_lines:
            product_id = move_line.product_id
            uom_id = move_line.product_uom
            move_line_ids = []
            for m in moves9[product_id.id]:
                move_line_id_d = {
                    'product_id': product_id.id,
                    'location_id': src_location_id.id,
                    'location_dest_id': dst_location_id.id,
                    'qty_done': m['quantity'],
                    'product_uom_id': uom_id.id,
                    'picking_id': picking_id.id,
                }
                if 'tracking_id' in m:
                    move_line_id_d.update({
                        'lot_id': m['tracking_id']
                    })
                move_line_ids.append(move_line_id_d)

            move_line.move_line_ids = [(0, False, v) for v in move_line_ids]

        if validate:
            picking_id.button_validate()

        return picking_id.id
