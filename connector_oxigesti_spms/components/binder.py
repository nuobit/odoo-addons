# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class OxigestiSPMStBinder(AbstractComponent):
    _name = "oxigesti.spms.binder"
    _inherit = ["connector.extension.generic.binder", "oxigesti.spms.connector"]
