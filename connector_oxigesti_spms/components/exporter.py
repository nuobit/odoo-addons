# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class OxigestiSPMSRecordDirectExporter(AbstractComponent):
    _name = "oxigesti.spms.record.direct.exporter"
    _inherit = [
        "connector.extension.generic.record.direct.exporter",
        "oxigesti.spms.connector",
    ]


class OxigestiSPMSBatchDelayedExporter(AbstractComponent):
    _name = "oxigesti.spms.batch.delayed.exporter"
    _inherit = [
        "connector.extension.generic.batch.delayed.exporter",
        "oxigesti.spms.connector",
    ]


class OxigestiSPMSBatchDirectExporter(AbstractComponent):
    _name = "oxigesti.spms.batch.direct.exporter"
    _inherit = [
        "connector.extension.generic.batch.direct.exporter",
        "oxigesti.spms.connector",
    ]
