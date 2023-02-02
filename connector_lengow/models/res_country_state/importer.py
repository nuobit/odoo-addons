# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class CountryStateBatchImporter(Component):
    """ Import the lengow Counties.

    For every county in the list, a delayed job is created.
    """
    _name = 'lengow.res.country.state.delayed.batch.importer'
    _inherit = 'lengow.delayed.batch.importer'

    _apply_on = 'lengow.res.country.state'


class CountryStateDirectBatchImporter(Component):
    """ Import the Lengow Counties.

    For every county in the list, import it directly.
    """
    _name = 'lengow.res.country.state.direct.batch.importer'
    _inherit = 'lengow.direct.batch.importer'

    _apply_on = 'lengow.res.country.state'


class CountryStateImporter(Component):
    _name = 'lengow.res.country.state.importer'
    _inherit = 'lengow.importer'

    _apply_on = 'lengow.res.country.state'
