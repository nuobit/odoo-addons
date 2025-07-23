# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component


class OxigestiSPMSResPartnerBatchDirectImporter(Component):
    _name = "oxigesti.spms.res.partner.batch.direct.importer"
    _inherit = "oxigesti.spms.batch.direct.importer"

    _apply_on = "oxigesti.spms.res.partner"


class OxigestiSPMSPartnerBatchDelayedImporter(Component):
    _name = "oxigesti.spms.res.partner.batch.delayed.importer"
    _inherit = "oxigesti.spms.batch.delayed.importer"

    _apply_on = "oxigesti.spms.res.partner"


class OxigestiSPMSResPartnerBatchRecordDirectImporter(Component):
    _name = "oxigesti.spms.res.partner.record.direct.importer"
    _inherit = "oxigesti.spms.record.direct.importer"

    _apply_on = "oxigesti.spms.res.partner"
