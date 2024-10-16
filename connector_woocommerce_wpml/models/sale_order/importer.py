# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class WooCommerceWPMLSaleOrderBatchDirectImporter(Component):
    """Import the WooCommerce Sale Order.

    For every Sale Order in the list, execute inmediately.
    """

    _name = "woocommerce.wpml.sale.order.batch.direct.importer"
    _inherit = "connector.extension.generic.batch.direct.importer"

    _apply_on = "woocommerce.wpml.sale.order"


class WooCommerceWPMLSaleOrderBatchDelayedImporter(Component):
    """Import the WooCommerce Sale Order.

    For every Sale Order in the list, a delayed job is created.
    """

    _name = "woocommerce.wpml.sale.order.batch.delayed.importer"
    _inherit = "connector.extension.generic.batch.delayed.importer"

    _apply_on = "woocommerce.wpml.sale.order"


class WooCommerceWPMLSaleOrderImporter(Component):
    _name = "woocommerce.wpml.sale.order.record.direct.importer"
    _inherit = "woocommerce.wpml.record.direct.importer"

    _apply_on = "woocommerce.wpml.sale.order"

    def _get_partner_parent_domain(self, dir_type, value):
        name = value[dir_type].get("company") or value[dir_type].get("name")
        return [
            ("company_type", "=", "company"),
            ("name", "=", name),
        ]

    def _additional_partner_parent_fields(self, value, dir_type):
        return {}

    def _get_partner_parent(self, dir_type, value):
        # TODO: REVIEW: slug for company name?
        domain = self._get_partner_parent_domain(dir_type, value)
        parent = self.env["res.partner"].search(domain)
        if not parent:
            parent = self.env["res.partner"].create(
                {
                    "name": value[dir_type].get("company")
                    or value[dir_type].get("name"),
                    "company_type": "company",
                    **self._additional_partner_parent_fields(value, dir_type),
                }
            )
            value[dir_type]["parent"] = parent.id
        elif len(parent) > 1:
            raise ValidationError(
                _("There are more than one partner with the same name")
            )
        value[dir_type]["parent"] = parent.id

    def _import_dependencies(self, external_data, sync_date):
        # Customer
        binder = self.binder_for("woocommerce.wpml.res.partner")
        billing = external_data.get("billing")
        if billing:
            self._get_partner_parent("billing", external_data)
            self._import_dependency(
                binder.dict2id(billing, in_field=False),
                "woocommerce.wpml.res.partner",
                sync_date,
                external_data=billing,
            )
        shipping = external_data.get("shipping")
        if shipping:
            self._get_partner_parent("shipping", external_data)
            self._import_dependency(
                binder.dict2id(shipping, in_field=False),
                "woocommerce.wpml.res.partner",
                sync_date,
                external_data=shipping,
            )
        # Products
        # We have done this so that a product can be linked with external id or sku
        #  without having to call the export dependency and thus avoid the write.
        #  Could we do it another way?
        products = external_data["products"]
        for product in products:
            if product["type"] == "simple":
                model = "product.template"
                if product["id"] == 0:
                    raise ValidationError(
                        _(
                            "The product '%s' in the order has been deleted on WooCommerce. "
                            "This order cannot be imported."
                        )
                        % product["name"]
                    )
            else:
                model = "product.product"
                if product["id"] == 0 and product["parent_id"] == 0:
                    raise ValidationError(
                        _(
                            "The product '%s' in the order has been deleted on WooCommerce. "
                            "This order cannot be imported."
                        )
                        % product["name"]
                    )

            binder = self.binder_for("woocommerce.wpml." + model)
            # external_id = binder.dict2id(product, in_field=False)
            # binding = binder.to_internal(external_id)
            # if not binding and product.get("sku"):
            #     relation = self.env[model].search(
            #         [("default_code", "=", product["sku"])]
            #     )
            #     if not relation:
            #         raise ValidationError(_("Product not found on Odoo"))
            #     if len(relation) > 1:
            #         raise ValidationError(
            #             _("More than one product found with sku %s") % product["sku"]
            #         )
            # TODO: Review not create a new product if not found
            self._import_dependency(
                binder.dict2id(product, in_field=False),
                "woocommerce.wpml." + model,
                sync_date,
                external_data=product,
            )
            #     binding = binder.bind_export(product, relation)
            # if not binding:
            #     raise ValidationError(_("Product not found on Odoo"))

    def _after_import(self, binding):
        sale_order = self.binder_for().unwrap_binding(binding)
        if (
            sale_order.state == "draft"
            and binding.woocommerce_wpml_status == "processing"
        ):
            sale_order.action_confirm()

    def _must_skip(self, binding):
        """Return True if the binding must be skipped."""
        res = super()._must_skip(binding)
        if binding:
            return _(
                "The Order %s is already imported "
                "-> Update not allowed"
                % self.binder_for().unwrap_binding(binding).display_name
            )
        return res


class WooCommerceWPMLSaleOrderChunkDirectImporter(Component):
    """Import the Woocommerce Orders.

    For every order in the list, import it directly.
    """

    _name = "woocommerce.wpml.sale.order.chunk.direct.importer"
    _inherit = "connector.extension.generic.chunk.direct.importer"

    _apply_on = "woocommerce.wpml.sale.order"


class WooCommerceWPMLSaleOrderChunkDelayedImporter(Component):
    """Import the Woocommerce Orders.

    For every order in the list, a delayed job is created.
    """

    _name = "woocommerce.wpml.sale.order.chunk.delayed.importer"
    _inherit = "connector.extension.generic.chunk.delayed.importer"

    _apply_on = "woocommerce.wpml.sale.order"
