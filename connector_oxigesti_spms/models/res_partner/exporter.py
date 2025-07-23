# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component


class OxigestiSPMSResPartnerDirectExporter(Component):
    _name = "oxigesti.spms.res.partner.direct.exporter"
    _inherit = "oxigesti.spms.record.direct.exporter"

    _apply_on = "oxigesti.spms.res.partner"


class OxigestiSPMSResPartnerBatchDelayedExporter(Component):
    _name = "oxigesti.spms.res.partner.batch.delayed.exporter"
    _inherit = "oxigesti.spms.batch.delayed.exporter"

    _apply_on = "oxigesti.spms.res.partner"


class OxigestiSPMSResPartnerBatchDirectExporter(Component):
    _name = "oxigesti.spms.res.partner.batch.direct.exporter"
    _inherit = "oxigesti.spms.batch.direct.exporter"

    _apply_on = "oxigesti.spms.res.partner"
