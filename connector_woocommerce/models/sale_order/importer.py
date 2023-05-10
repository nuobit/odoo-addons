# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class WooCommerceSaleOrderBatchDirectImporter(Component):
    """Import the WooCommerce Sale Order.

    For every Sale Order in the list, execute inmediately.
    """

    _name = "woocommerce.sale.order.batch.direct.importer"
    _inherit = "woocommerce.batch.direct.importer"

    _apply_on = "woocommerce.sale.order"


class WooCommerceSaleOrderBatchDelayedImporter(Component):
    """Import the WooCommerce Sale Order.

    For every Sale Order in the list, a delayed job is created.
    """

    _name = "woocommerce.sale.order.batch.delayed.importer"
    _inherit = "woocommerce.batch.delayed.importer"

    _apply_on = "woocommerce.sale.order"


class WooCommerceSaleOrderImporter(Component):
    _name = "woocommerce.sale.order.record.direct.importer"
    _inherit = "woocommerce.record.direct.importer"

    _apply_on = "woocommerce.sale.order"

    def _import_dependencies(self, external_data):
        # Customer
        binder = self.binder_for("woocommerce.res.partner")
        billing = external_data.get("billing")
        if billing:
            self._import_dependency(
                binder.dict2id(billing, in_field=False),
                "woocommerce.res.partner",
                external_data=billing,
                always=False,
            )
        shipping = external_data.get("shipping")
        if shipping:
            self._import_dependency(
                binder.dict2id(shipping, in_field=False),
                "woocommerce.res.partner",
                external_data=shipping,
                always=False,
            )
        # Products
        # TODO: REVIAR-- hem fet aixo de manera que es pugui enllaçar un producte amb id extern
        #  o amb sku sense haver de cridar al export dependency i evitar aixi els write.
        #  Ho podriem fer d'una altra manera?
        products = external_data["products"]
        for product in products:
            model = (
                "product.template" if product["type"] == "simple" else "product.product"
            )
            binder = self.binder_for("woocommerce." + model)
            external_id = binder.dict2id(product, in_field=False)
            binding = binder.to_internal(external_id)
            if not binding and product.get("sku"):
                relation = self.env[model].search(
                    [("default_code", "=", product["sku"])]
                )
                if not relation:
                    raise ValidationError(_("Product not found on Odoo"))
                if len(relation) > 1:
                    raise ValidationError(
                        _("More than one product found with sku %s") % product["sku"]
                    )
                binding = binder.bind_export(product, relation)
            if not binding:
                raise ValidationError(_("Product not found on Odoo"))

    # def _after_import(self, binding):
    #     sale_order = self.binder_for().unwrap_binding(binding)
        # for line in sale_order.order_line:
        #     line._compute_tax_id()
        #
        # ## order cancel
        # if binding.lengow_status == 'canceled':
        #     sale_order.action_cancel()
        # else:
        #     ## order validation
        #     sale_order.action_confirm()

class WooCommerceSaleOrderChunkDelayedImporter(Component):
    """Import the Woocommerce Orders.

    For every order in the list, a delayed job is created.
    """

    _name = "woocommerce.sale.order.chunk.delayed.importer"
    _inherit = "woocommerce.chunk.delayed.importer"

    _apply_on = "woocommerce.sale.order"


class WooCommerceSaleOrderChunkDirectImporter(Component):
    """Import the Woocommerce Orders.

    For every order in the list, import it directly.
    """

    _name = "woocommerce.sale.order.chunk.direct.importer"
    _inherit = "woocommerce.chunk.direct.importer"

    _apply_on = "woocommerce.sale.order"
