# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SPMSLot(models.Model):
    _inherit = "spms.lot"

    oxigesti_spms_bind_ids = fields.One2many(
        string="Oxigesti SPMS Binding",
        comodel_name="oxigesti.spms.spms.lot",
        inverse_name="odoo_id",
        help="Oxigesti SPMS Bindings for this partner",
    )
