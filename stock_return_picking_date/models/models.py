from openerp import models, fields, api, _

class stock_return_picking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.multi
    def _create_returns(self):
        self.ensure_one()
        new_picking_id, pick_type_id = super(stock_return_picking, self)._create_returns()

        new_picking_obj = self.env['stock.picking'].browse(new_picking_id)

        cur_date = fields.Datetime.from_string(new_picking_obj.date)
        cur_min_date = fields.Datetime.from_string(new_picking_obj.min_date)
        new_picking_obj.date = fields.datetime.now()

        new_picking_obj.min_date = fields.Datetime.from_string(new_picking_obj.date) + (cur_min_date - cur_date)
        new_picking_obj.max_date = new_picking_obj.min_date


        return new_picking_id, pick_type_id