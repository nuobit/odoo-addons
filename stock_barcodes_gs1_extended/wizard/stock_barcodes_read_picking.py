# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class WizStockBarcodesReadPicking(models.TransientModel):
    _inherit = 'wiz.stock.barcodes.read.picking'

    picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Picking type',
        readonly=True,
    )

    def _prepare_stock_moves_domain(self):
        domain = super(WizStockBarcodesReadPicking, self)._prepare_stock_moves_domain()
        domain.append([
            ('picking_id.picking_type_id', '=', self.picking_type_id.id),
        ])
        return domain
