# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ResPartnerDelayedBatchExporter(Component):
    """Export the SAP B1 Partners.

    For every partner in the list, a delayed job is created.
    """

    _name = "sapb1.res.partner.delayed.batch.exporter"
    _inherit = "sapb1.delayed.batch.exporter"

    _apply_on = "sapb1.res.partner"


class ResPartnerDirectBatchExporter(Component):
    """Export the SAP B1 Partners.

    For every partner in the list, export it directly.
    """

    _name = "sapb1.res.partner.direct.batch.exporter"
    _inherit = "sapb1.direct.batch.exporter"

    _apply_on = "sapb1.res.partner"


class ResPartnerExporter(Component):
    _name = "sapb1.res.partner.exporter"
    _inherit = "sapb1.exporter"

    _apply_on = "sapb1.res.partner"
