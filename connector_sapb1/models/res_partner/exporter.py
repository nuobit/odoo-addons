# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class SAPB1ResPartnerBatchDirectExporter(Component):
    """Export the SAP B1 Partners.

    For every partner in the list, export it directly.
    """

    _name = "sapb1.res.partner.batch.direct.exporter"
    _inherit = "connector.extension.generic.batch.direct.exporter"

    _apply_on = "sapb1.res.partner"


class SAPB1ResPartnerBatchDelayedExporter(Component):
    """Export the SAP B1 Partners.

    For every partner in the list, a delayed job is created.
    """

    _name = "sapb1.res.partner.batch.delayed.exporter"
    _inherit = "connector.extension.generic.batch.delayed.exporter"

    _apply_on = "sapb1.res.partner"


class SAPB1ResPartnerExporter(Component):
    _name = "sapb1.res.partner.record.direct.exporter"
    _inherit = "sapb1.record.direct.exporter"

    _apply_on = "sapb1.res.partner"
