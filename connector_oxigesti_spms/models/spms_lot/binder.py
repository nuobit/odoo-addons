# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class SPMSLotBinder(Component):
    _name = "oxigesti.spms.spms.lot.binder"
    _inherit = "oxigesti.spms.binder"

    _apply_on = "oxigesti.spms.spms.lot"

    external_id = "Id"
    internal_id = "oxigesti_spms_id"
    internal_alt_id = ["name"]
    external_alt_id = ["Nome"]
