# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class RepairOrder(models.Model):
    _inherit = "repair.order"

    def action_invoice_create(self):
        """Override to link repair order to the created invoice"""
        result = super().action_invoice_create()
        
        # Link this repair order to any invoices created
        self._link_to_invoices()
        
        return result

    def _link_to_invoices(self):
        """Link repair order to related invoices"""
        # Find invoices related to this repair order
        invoices = self.env['account.move'].search([
            ('invoice_origin', '=', self.name),
            ('repair_order_id', '=', False),  # Only link if not already linked
            ('move_type', 'in', ['out_invoice', 'in_invoice']),
        ])
        
        # Also check for invoices with this repair order in the origin field
        if not invoices:
            invoices = self.env['account.move'].search([
                ('invoice_origin', 'ilike', self.name),
                ('repair_order_id', '=', False),
                ('move_type', 'in', ['out_invoice', 'in_invoice']),
            ])
        
        # Link the invoices to this repair order
        for invoice in invoices:
            invoice.repair_order_id = self.id

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to link existing invoices if any"""
        repairs = super().create(vals_list)
        for repair in repairs:
            repair._link_to_invoices()
        return repairs