# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class SaleOrderImportMapChild(Component):
    _name = "woocommerce.sale.order.map.child.import"
    _inherit = "woocommerce.map.child.import"

    _apply_on = "woocommerce.sale.order.line"

    def get_item_values(self, map_record, to_attr, options):
        binder = self.binder_for("woocommerce.sale.order.line")
        external_id = binder.dict2id(map_record.source, in_field=False)
        woocommerce_order_line = binder.to_internal(external_id, unwrap=False)
        if woocommerce_order_line:
            map_record.update(id=woocommerce_order_line.id)
        return map_record.values(**options)

    def format_items(self, items_values):
        ops = []
        for values in items_values:
            _id = values.pop("id", None)
            if _id:
                ops.append((1, _id, values))
            else:
                ops.append((0, False, values))
        return ops


class WooCommerceSaleOrderImportMapper(Component):
    _name = "woocommerce.sale.order.import.mapper"
    _inherit = "woocommerce.import.mapper"

    _apply_on = "woocommerce.sale.order"
    children = [
        ("line_items", "woocommerce_order_line_ids", "woocommerce.sale.order.line")
    ]

    def _get_billing_partner(self, record):
        binder = self.binder_for("woocommerce.res.partner")
        external_id = binder.dict2id(record["billing"], in_field=False)
        partner = binder.to_internal(external_id, unwrap=True)
        assert partner, (
            "partner_id %s should have been imported in "
            "SaleOrderImporter._import_dependencies" % external_id
        )
        return partner

    @mapping
    def billing(self, record):
        if record["billing"]:
            partner = self._get_billing_partner(record)
            if not partner.active:
                raise ValidationError(
                    _("The partner %s, with id:%s is archived, please, enable it")
                    % (partner.name, partner.id)
                )
            return {
                "partner_id": (partner.parent_id or partner).id,
                "partner_invoice_id": partner.id,
            }

    @mapping
    def shipping(self, record):
        if record["shipping"]:
            binder = self.binder_for("woocommerce.res.partner")
            external_id = binder.dict2id(record["shipping"], in_field=False)
            partner = binder.to_internal(external_id, unwrap=True)
            assert partner, (
                "partner_shipping_id %s should have been imported in "
                "SaleOrderImporter._import_dependencies" % external_id
            )
            return {"partner_shipping_id": partner.id}

    @mapping
    def payment_method(self, record):
        payment_mode = self.backend_record.payment_mode_ids.filtered(
            lambda x: record["payment_method"] == x.woocommerce_payment_mode
        )
        if not payment_mode and record["payment_method"]:
            raise ValidationError(
                _("Payment method '%s' is not defined on backend")
                % record.get("payment_method")
            )
        return {"payment_mode_id": payment_mode.payment_mode_id.id}

    def _get_currency(self, record):
        currency = self.env["res.currency"].search([("name", "=", record["currency"])])
        if not currency:
            raise ValidationError(
                _("Currency '%s' is not defined") % record["currency"]
            )
        return currency

    @mapping
    def currency(self, record):
        return {"currency_id": self._get_currency(record).id}

    @only_create
    @mapping
    def pricelist(self, record):
        # The shop's prices come from the discount pricelist, so the order
        # carries it; without one, it carries the pricelist Odoo would give it,
        # its partner's. It is Odoo's choice, not shop data, so an update
        # leaves it alone.
        pricelist = self.backend_record.discount_pricelist_id
        if not pricelist and record["billing"]:
            partner = self._get_billing_partner(record)
            pricelist = (partner.parent_id or partner).property_product_pricelist

        if not pricelist:
            raise ValidationError(
                _(
                    "The WooCommerce order %s gets no pricelist: set a discount "
                    "pricelist on the backend."
                )
                % record["id"]
            )
        # Odoo gives the order the currency of its pricelist, whatever the
        # currency of the WooCommerce order, so both have to be the same.
        currency = self._get_currency(record)
        if pricelist.currency_id != currency:
            raise ValidationError(
                _(
                    "The WooCommerce order %(order)s is in %(order_currency)s, but "
                    "its pricelist '%(pricelist)s' is in %(pricelist_currency)s: set "
                    "a discount pricelist in %(order_currency)s on the backend."
                )
                % {
                    "order": record["id"],
                    "order_currency": currency.name,
                    "pricelist": pricelist.name,
                    "pricelist_currency": pricelist.currency_id.name,
                }
            )
        return {"pricelist_id": pricelist.id}

    @mapping
    def woocommerce_order_id(self, record):
        client_order_ref = (
            self.backend_record.client_order_ref_prefix + "-" + str(record["id"])
        )
        return {"client_order_ref": client_order_ref}

    @mapping
    def note(self, record):
        return {"note": record["customer_note"]}

    @mapping
    def status(self, record):
        return {"woocommerce_status": record["status"]}

    @only_create
    @mapping
    def is_woocommerce(self, record):
        return {"is_woocommerce": True}
