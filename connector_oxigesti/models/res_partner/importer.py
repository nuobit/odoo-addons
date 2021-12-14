# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class ResPartnerDelayedBatchImporter(Component):
    """Import the Oxigesti Partners.

    For every partner in the list, a delayed job is created.
    """

    _name = "oxigesti.res.partner.delayed.batch.importer"
    _inherit = "oxigesti.delayed.batch.importer"

    _apply_on = "oxigesti.res.partner"


class ResPartnerDirectBatchImporter(Component):
    """Import the Oxigesti Partners.

    For every partner in the list, import it directly.
    """

    _name = "oxigesti.res.partner.direct.batch.importer"
    _inherit = "oxigesti.direct.batch.importer"

    _apply_on = "oxigesti.res.partner"


class ResPartnerImporter(Component):
    _name = "oxigesti.res.partner.importer"
    _inherit = "oxigesti.importer"

    _apply_on = "oxigesti.res.partner"
