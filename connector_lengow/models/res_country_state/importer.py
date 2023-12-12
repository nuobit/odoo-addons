# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class LengowCountryStateDirectBatchImporter(Component):
    """Import the Lengow Counties.

    For every county in the list, import it directly.
    """

    _name = "lengow.res.country.state.batch.direct.importer"
    _inherit = "connector.extension.generic.batch.direct.importer"

    _apply_on = "lengow.res.country.state"


class LengowCountryStateBatchDelayedImporter(Component):
    """Import the lengow Counties.

    For every county in the list, a delayed job is created.
    """

    _name = "lengow.res.country.state.batch.delayed.importer"
    _inherit = "connector.extension.generic.batch.delayed.importer"

    _apply_on = "lengow.res.country.state"


class LengowCountryStateImporter(Component):
    _name = "lengow.res.country.state.record.direct.importer"
    _inherit = "lengow.record.direct.importer"

    _apply_on = "lengow.res.country.state"
