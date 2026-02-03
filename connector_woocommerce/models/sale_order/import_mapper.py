# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
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

    @mapping
    def billing(self, record):
        if record["billing"]:
            binder = self.binder_for("woocommerce.res.partner")
            external_id = binder.dict2id(record["billing"], in_field=False)
            partner = binder.to_internal(external_id, unwrap=True)
            assert partner, (
                "partner_id %s should have been imported in "
                "SaleOrderImporter._import_dependencies" % external_id
            )
            if not partner.active:
                raise ValidationError(
                    _("The partner %s, with id:%s is archived, please, enable it")
                    % (partner.name, partner.id)
                )
            partner_return = {"partner_invoice_id": partner.id}
            if partner.parent_id:
                partner_return["partner_id"] = partner.parent_id.id
            else:
                partner_return["partner_id"] = partner.id
            return partner_return

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

    @mapping
    def currency(self, record):
        currency = self.env["res.currency"].search(
            [("name", "=", record.get("currency"))]
        )
        if not currency:
            raise ValidationError(
                _("Currency '%s' is not defined") % record.get("currency")
            )
        return {"currency_id": currency.id}

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
