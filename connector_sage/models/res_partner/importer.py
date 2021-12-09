# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class ResPartnerBatchImporter(Component):
    """Import the Sage Partners.

    For every partner in the list, a delayed job is created.
    """

    _name = "sage.res.partner.delayed.batch.importer"
    _inherit = "sage.delayed.batch.importer"
    _apply_on = "sage.res.partner"


class ResPartnerImporter(Component):
    _name = "sage.res.partner.importer"
    _inherit = "sage.importer"
    _apply_on = "sage.res.partner"
