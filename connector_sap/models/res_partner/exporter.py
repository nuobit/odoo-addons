# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ResPartnerDelayedBatchImporter(Component):
    """ Import the SAPB! Partners.

    For every partner in the list, a delayed job is created.
    """
    _name = 'sap.res.partner.delayed.batch.exporter'
    _inherit = 'sap.delayed.batch.exporter'

    _apply_on = 'sap.res.partner'


class ResPartnerDirectBatchExporter(Component):
    """ Import the SAPB1 Partners.

    For every partner in the list, import it directly.
    """
    _name = 'sap.res.partner.direct.batch.exporter'
    _inherit = 'sap.direct.batch.exporter'

    _apply_on = 'sap.res.partner'


class ResPartnerExporter(Component):
    _name = 'sap.res.partner.exporter'
    _inherit = 'sap.exporter'

    _apply_on = 'sap.res.partner'
