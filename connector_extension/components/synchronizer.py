# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo.addons.component.core import AbstractComponent


class ConnectorExtensionSynchronizer(AbstractComponent):
    _name = "connector.extension.synchronizer"
    _inherit = "base.synchronizer"

    #: usage of the component used as backend adapter,
    #: customized to use "adapter" instead of "backend.adapter"
    _base_backend_adapter_usage = "adapter"
    _description = "Connector Extension Base Synchronizer Component"
