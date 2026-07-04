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

    def _must_skip(self, binding, external_data):
        """Skip the buyer import on anonymized re-syncs of existing orders.

        Marketplaces re-send old orders with the buyer contact erased
        (GDPR anonymization), sometimes together with a legitimate order
        update (e.g. a refund). The contact name is part of the partner
        identity (it feeds the address hash used by both binder keys), so
        an erased name can never resolve to the partner created at first
        import: letting the import proceed would try to create a nameless
        duplicate and fail the whole order update in the name mapping.
        The order keeps pointing to the partners of its first import, so
        there is nothing to import here - skip, and let the order update
        land.

        This cannot be solved upstream: filtering those orders out at
        download would eat the legitimate update they carry, and the
        payload anonymized flag lags the actual data wipe, so the erased
        name itself is the only reliable signal at import time.

        Only re-syncs are skipped (the order must already exist): the
        first import of an order with an empty contact name still fails
        loudly in the partner mapper, because there a real partner must
        be created and there is no data to create it with - that is a
        configuration or source-data problem to surface, not to skip.
        """
        if not binding and not (external_data.get("complete_name") or "").strip():
            order_binder = self.binder_for("lengow.sale.order")
            order_external_id = order_binder.dict2id(external_data, in_field=False)
            if order_binder.is_complete_id(
                order_external_id, in_field=False
            ) and order_binder.to_internal(order_external_id):
                return _(
                    "Skipped %(address_type)s address of order %(order)s "
                    "(marketplace %(marketplace)s): the contact name was "
                    "erased upstream (anonymized re-sync) and the order "
                    "keeps the partners of its first import."
                ) % {
                    "address_type": external_data.get("type"),
                    "order": external_data.get("marketplace_order_id"),
                    "marketplace": external_data.get("marketplace"),
                }
        return super()._must_skip(binding, external_data)

    def _import_dependencies(self, external_data, sync_date):
        # County
        model = "lengow.res.country.state"
        binder = self.binder_for(model)
        external_id = binder.dict2id(external_data, in_field=False)
        if binder.is_complete_id(external_id, in_field=False):
            self._import_dependency(
                external_id, model, sync_date, external_data=external_data, always=False
            )
