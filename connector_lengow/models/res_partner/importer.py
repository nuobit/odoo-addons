# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.exceptions import ValidationError


class ResPartnerDelayedBatchImporter(Component):
    """ Import the lengow Partners.

    For every partner in the list, a delayed job is created.
    """
    _name = 'lengow.res.partner.delayed.batch.importer'
    _inherit = 'lengow.delayed.batch.importer'

    _apply_on = 'lengow.res.partner'


class ResPartnerDirectBatchImporter(Component):
    """ Import the Lengow Partners.

    For every partner in the list, import it directly.
    """
    _name = 'lengow.res.partner.direct.batch.importer'
    _inherit = 'lengow.direct.batch.importer'

    _apply_on = 'lengow.res.partner'


class ResPartnerImporter(Component):
    _name = 'lengow.res.partner.importer'
    _inherit = 'lengow.importer'

    _apply_on = 'lengow.res.partner'

    def run(self, external_id, external_data, external_fields=None):
        if not external_data:
            raise ValidationError("External data is mandatory")
        return super().run(external_id, external_data=external_data)
