# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class LengowResPartnerBatchDirectImporter(Component):
    """Import the Lengow Partners.

    For every partner in the list, import it directly.
    """

    _name = "lengow.res.partner.batch.direct.importer"
    _inherit = "connector.extension.generic.batch.direct.importer"

    _apply_on = "lengow.res.partner"


class LengowResPartnerBatchDelayedImporter(Component):
    """Import the lengow Partners.

    For every partner in the list, a delayed job is created.
    """

    _name = "lengow.res.partner.batch.delayed.importer"
    _inherit = "connector.extension.generic.batch.delayed.importer"

    _apply_on = "lengow.res.partner"


class LengowResPartnerImporter(Component):
    _name = "lengow.res.partner.record.direct.importer"
    _inherit = "lengow.record.direct.importer"

    _apply_on = "lengow.res.partner"

    def run(self, external_id, sync_date, external_data=None, external_fields=None):
        if not external_data:
            raise ValidationError(_("External data is mandatory"))
        return super().run(external_id, sync_date, external_data=external_data)

    def _import_dependencies(self, external_data, sync_date):
        # County
        model = "lengow.res.country.state"
        binder = self.binder_for(model)
        external_id = binder.dict2id(external_data, in_field=False)
        if binder.is_complete_id(external_id, in_field=False):
            self._import_dependency(
                external_id, model, sync_date, external_data=external_data, always=False
            )
