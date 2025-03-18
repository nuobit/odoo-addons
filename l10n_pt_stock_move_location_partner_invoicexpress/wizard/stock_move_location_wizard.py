# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import ValidationError


class StockMoveLocationWizard(models.TransientModel):
    _inherit = "wiz.stock.move.location"

    def _create_picking(self):
        picking = super()._create_picking()
        if (
            picking.partner_id.country_id.code == "PT"
            and self.picking_type_id.company_id.has_invoicexpress
        ):
            if self.picking_type_id.invoicexpress_doc_type:
                raise ValidationError(
                    _(
                        "The InvoiceExpress Doc Type is defined in the Operation type. "
                        "It was expected to be blank, please remove it."
                    )
                )
            picking.invoicexpress_doc_type = "transport"
        return picking
