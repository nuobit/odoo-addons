# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class OxigestiSpmsBatchDirectImporter(AbstractComponent):
    _name = "oxigesti.spms.batch.direct.importer"
    _inherit = [
        "connector.extension.generic.batch.direct.importer",
        "oxigesti.spms.connector",
    ]


class OxigestiSPMSBatchDelayedImporter(AbstractComponent):
    _name = "oxigesti.spms.batch.delayed.importer"
    _inherit = [
        "connector.extension.generic.batch.delayed.importer",
        "oxigesti.spms.connector",
    ]


class OxigestiSPMSRecordDirectImporter(AbstractComponent):
    _name = "oxigesti.spms.record.direct.importer"
    _inherit = [
        "connector.extension.generic.record.direct.importer",
        "oxigesti.spms.connector",
    ]
