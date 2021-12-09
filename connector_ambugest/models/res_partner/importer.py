# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class ResPartnerBatchImporter(Component):
    """Import the Ambugest Partners.

    For every partner in the list, a delayed job is created.
    """

    _name = "ambugest.res.partner.delayed.batch.importer"
    _inherit = "ambugest.delayed.batch.importer"
    _apply_on = "ambugest.res.partner"


class ResPartnerImporter(Component):
    _name = "ambugest.res.partner.importer"
    _inherit = "ambugest.importer"
    _apply_on = "ambugest.res.partner"
