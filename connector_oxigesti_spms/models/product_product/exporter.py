# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component


class OxigestiSPMSProductProductDirectExporter(Component):
    _name = "oxigesti.spms.product.product.direct.exporter"
    _inherit = "oxigesti.spms.record.direct.exporter"

    _apply_on = "oxigesti.spms.product.product"


class OxigestiSPMSProductProductBatchDelayedExporter(Component):
    _name = "oxigesti.spms.product.product.batch.delayed.exporter"
    _inherit = "oxigesti.spms.batch.delayed.exporter"

    _apply_on = "oxigesti.spms.product.product"


class OxigestiSPMSProductProductBatchDirectExporter(Component):
    _name = "oxigesti.spms.product.product.batch.direct.exporter"
    _inherit = "oxigesti.spms.batch.direct.exporter"

    _apply_on = "oxigesti.spms.product.product"
