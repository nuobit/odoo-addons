# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class LengowSaleOrderBatchDirectImporter(Component):
    """Import the Lengow Partners.

    For every partner in the list, import it directly.
    """

    _name = "lengow.sale.order.batch.direct.importer"
    _inherit = "connector.extension.generic.batch.direct.importer"

    _apply_on = "lengow.res.partner"


class LengowSaleOrderBatchDelayedImporter(Component):
    """Import the Lengow Services.

    For every sale order in the list, a delayed job is created.
    """

    _name = "lengow.sale.order.batch.delayed.importer"
    _inherit = "connector.extension.generic.batch.delayed.importer"

    _apply_on = "lengow.sale.order"


class LengowSaleOrderImporter(Component):
    _name = "lengow.sale.order.importer"
    _inherit = "lengow.record.direct.importer"

    _apply_on = "lengow.sale.order"

    def _import_dependencies(self, external_data, sync_date):
        # Customer
        billing_address = external_data["billing_address"]
        binder = self.binder_for("lengow.res.partner")
        if billing_address:
            self._import_dependency(
                binder.dict2id(billing_address, in_field=False),
                "lengow.res.partner",
                sync_date,
                external_data=billing_address,
                always=False,
            )
        delivery_address = external_data["delivery_address"]
        if delivery_address:
            self._import_dependency(
                binder.dict2id(delivery_address, in_field=False),
                "lengow.res.partner",
                sync_date,
                external_data=delivery_address,
                always=False,
            )
        # Products
        order_lines = external_data["items"]
        for line in order_lines:
            if not line["is_shipping"]:
                if line["sku"]:
                    self._import_dependency(
                        line["sku"],
                        "lengow.product.product",
                        sync_date,
                        external_data={"sku": line["sku"]},
                        always=False,
                    )
                elif line["marketplace_product_id"]:
                    self._import_dependency(
                        line["marketplace_product_id"],
                        "lengow.product.product",
                        sync_date,
                        external_data={"sku": line["marketplace_product_id"]},
                        always=False,
                    )
                else:
                    raise ValidationError(
                        _("No sku or marketplace_product_id for line %s") % line
                    )

    def _after_import(self, binding):
        sale_order = self.binder_for().unwrap_binding(binding)
        for line in sale_order.order_line:
            line._compute_tax_id()

        # order cancel
        if binding.lengow_status == "canceled":
            sale_order.action_cancel()
        else:
            # order validation
            sale_order.with_context(confirm_from_lengow=True).action_confirm()

    def _update(self, binding, values):
        return super()._update(binding.with_context(export_from_lengow=True), values)
