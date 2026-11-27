# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class WooCommerceSaleOrderBatchDirectImporter(Component):
    """Import the WooCommerce Sale Order.

    For every Sale Order in the list, execute inmediately.
    """

    _name = "woocommerce.sale.order.batch.direct.importer"
    _inherit = "connector.extension.generic.batch.direct.importer"

    _apply_on = "woocommerce.sale.order"


class WooCommerceSaleOrderBatchDelayedImporter(Component):
    """Import the WooCommerce Sale Order.

    For every Sale Order in the list, a delayed job is created.
    """

    _name = "woocommerce.sale.order.batch.delayed.importer"
    _inherit = "connector.extension.generic.batch.delayed.importer"

    _apply_on = "woocommerce.sale.order"


class WooCommerceSaleOrderImporter(Component):
    _name = "woocommerce.sale.order.record.direct.importer"
    _inherit = "woocommerce.record.direct.importer"

    _apply_on = "woocommerce.sale.order"

    def _get_partner_parent_key(self, dir_type, value):
        """The field and the value that find the contact of the ``dir_type``
        block of ``value``: the name of its company, else its own."""
        return "name", value[dir_type].get("company") or value[dir_type].get("name")

    def _get_partner_parent_domain(self, dir_type, value):
        field, key = self._get_partner_parent_key(dir_type, value)
        return [
            ("child_ids", "!=", False),
            (field, "=", key),
        ]

    def _additional_partner_parent_fields(self, value, dir_type):
        return {}

    def _search_partner_parent(self, dir_type, value):
        """The contact the ``dir_type`` block of ``value`` belongs to, or none.
        More than one is refused, each of them listed."""
        parents = self.env["res.partner"].search(
            self._get_partner_parent_domain(dir_type, value)
        )
        if len(parents) > 1:
            field, key = self._get_partner_parent_key(dir_type, value)
            raise ValidationError(
                _(
                    "%(count)s contacts have the %(field)s %(value)s, which must "
                    "belong to one contact only:"
                )
                % {
                    "count": len(parents),
                    "field": parents.fields_get([field], ["string"])[field]["string"],
                    "value": key,
                }
                + "".join(
                    "\n- %s %s" % (parent.id, parent.display_name)
                    for parent in parents.sorted("id")
                )
            )
        return parents

    def _get_partner_parent_sales_values(self, value):
        """The sales values of a new customer of the order ``value``: the
        backend's discount pricelist and the order's payment mode. A value the
        backend or the order does not have is left out, so the customer keeps
        the default Odoo gives it."""
        sales_values = {
            "property_product_pricelist": self.backend_record.discount_pricelist_id,
            "customer_payment_mode_id": self.backend_record._get_payment_mode(
                value["payment_method"]
            ),
        }
        return {field: record.id for field, record in sales_values.items() if record}

    def _get_partner_parent_values(self, dir_type, value):
        """The values of a new contact for the ``dir_type`` block of ``value``:
        named after the block's company, else its buyer, with the address,
        the phone and the e-mail its own address gets from the block, and the
        sales values of a new customer."""
        # TODO: REVIEW: slug for company name?
        name = value[dir_type]["company"] or value[dir_type]["name"]
        if not name:
            raise ValidationError(
                _(
                    "Cannot create the parent partner for %s: %s because neither "
                    "company nor name is set."
                )
                % (dir_type, value)
            )
        address_values = (
            self.component(usage="import.mapper", model_name="woocommerce.res.partner")
            .map_record(value[dir_type])
            .values(for_create=True)
        )
        # The mapper leaves out a state or a country Odoo does not have
        customer_fields = self.env["res.partner"]._address_fields() + [
            "phone",
            "email",
        ]
        return {
            "name": name,
            "company_type": "company",
            **{
                field: address_values[field]
                for field in customer_fields
                if field in address_values
            },
            **self._get_partner_parent_sales_values(value),
            **self._additional_partner_parent_fields(value, dir_type),
        }

    def _create_partner_parent(self, dir_type, value):
        """Create the contact the ``dir_type`` block of ``value`` belongs to."""
        return self.env["res.partner"].create(
            self._get_partner_parent_values(dir_type, value)
        )

    def _get_order_customer(self, external_data):
        """The order's customer. A billing block already imported gives it
        through its binding, as the order's mapper does: the parent of its
        address, or the address itself when it has none. Any other block is
        searched for, and gets a new customer when nothing is found."""
        binder = self.binder_for("woocommerce.res.partner")
        # The binding's unique key binds a block to one address at most
        address = binder.to_internal(
            binder.dict2id(external_data["billing"], in_field=False), unwrap=True
        )
        if address:
            customer = address.parent_id or address
        else:
            customer = self._search_partner_parent(
                "billing", external_data
            ) or self._create_partner_parent("billing", external_data)
        return customer

    def _import_dependencies(self, external_data, sync_date):
        # Customer: both addresses hang from it. A shop order always has a
        # billing block; the adapter sets the shipping block to None when the
        # order has none.
        binder = self.binder_for("woocommerce.res.partner")
        customer = self._get_order_customer(external_data)
        billing = external_data["billing"]
        billing["parent"] = customer.id
        self._import_dependency(
            binder.dict2id(billing, in_field=False),
            "woocommerce.res.partner",
            sync_date,
            external_data=billing,
        )
        shipping = external_data["shipping"]
        if shipping is not None:
            shipping["parent"] = customer.id
            self._import_dependency(
                binder.dict2id(shipping, in_field=False),
                "woocommerce.res.partner",
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

            binder = self.binder_for("woocommerce." + model)
            external_id = binder.dict2id(product, in_field=False)
            binding = binder.to_internal(external_id)
            if not binding and product.get("sku"):
                relation = self.env[model].search(
                    [("default_code", "=", product["sku"])]
                )
                if not relation:
                    raise ValidationError(
                        _("Product with sku %s not found on Odoo") % product["sku"]
                    )
                if len(relation) > 1:
                    raise ValidationError(
                        _("More than one product found with sku %s") % product["sku"]
                    )
                binding = binder.bind_export(product, relation)
            if not binding:
                raise ValidationError(_("Product not found on Odoo"))

    def _after_import(self, binding):
        sale_order = self.binder_for().unwrap_binding(binding)
        if sale_order.state == "draft" and binding.woocommerce_status == "processing":
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


class WooCommerceSaleOrderChunkDirectImporter(Component):
    """Import the Woocommerce Orders.

    For every order in the list, import it directly.
    """

    _name = "woocommerce.sale.order.chunk.direct.importer"
    _inherit = "connector.extension.generic.chunk.direct.importer"

    _apply_on = "woocommerce.sale.order"


class WooCommerceSaleOrderChunkDelayedImporter(Component):
    """Import the Woocommerce Orders.

    For every order in the list, a delayed job is created.
    """

    _name = "woocommerce.sale.order.chunk.delayed.importer"
    _inherit = "connector.extension.generic.chunk.delayed.importer"

    _apply_on = "woocommerce.sale.order"
