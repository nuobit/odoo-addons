# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class SaleOrderBatchImporter(Component):
    """Import the Lengow Services.

    For every sale order in the list, a delayed job is created.
    """

    _name = "lengow.sale.order.delayed.batch.importer"
    _inherit = "lengow.delayed.batch.importer"

    _apply_on = "lengow.sale.order"


class SaleOrderImporter(Component):
    _name = "lengow.sale.order.importer"
    _inherit = "lengow.importer"

    _apply_on = "lengow.sale.order"

    def _import_dependencies(self, external_data):
        # Customer
        billing_address = external_data["billing_address"]
        binder = self.binder_for("lengow.res.partner")
        if billing_address:
            self._import_dependency(
                binder.dict2id(billing_address, in_field=False),
                "lengow.res.partner",
                external_data=billing_address,
                always=False,
            )
        delivery_address = external_data["delivery_address"]
        if delivery_address:
            self._import_dependency(
                binder.dict2id(delivery_address, in_field=False),
                "lengow.res.partner",
                external_data=delivery_address,
                always=False,
            )
        # Products
        order_lines = external_data["items"]
        for line in order_lines:
            if not line["is_shipping"]:
                self._import_dependency(
                    line["sku"],
                    "lengow.product.product",
                    external_data={"sku": line["sku"]},
                    always=False,
                )

    def _after_import(self, binding):
        sale_order = self.binder_for().unwrap_binding(binding)
        for line in sale_order.order_line:
            line._compute_tax_id()

        ## order cancel
        if binding.lengow_status == "canceled":
            sale_order.action_cancel()
        else:
            ## order validation
            sale_order.action_confirm()
