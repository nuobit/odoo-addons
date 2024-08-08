# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class SaleOrderImportMapChild(Component):
    _name = "lengow.sale.order.map.child.import"
    _inherit = "lengow.map.child.import"

    _apply_on = "lengow.sale.order.line"

    def get_item_values(self, map_record, to_attr, options):
        binder = self.binder_for("lengow.sale.order.line")
        external_id = binder.dict2id(map_record.source, in_field=False)
        lengow_order_line = binder.to_internal(external_id, unwrap=False)
        if lengow_order_line:
            map_record.update(id=lengow_order_line.id)
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


class SaleOrderImportMapper(Component):
    _name = "lengow.sale.order.import.mapper"
    _inherit = "lengow.import.mapper"

    _apply_on = "lengow.sale.order"

    children = [("items", "lengow_order_line_ids", "lengow.sale.order.line")]

    @only_create
    @mapping
    def company_id(self, record):
        return {"company_id": self.backend_record.company_id.id}

    @mapping
    def delivery_address(self, record):
        if record["delivery_address"]:
            binder = self.binder_for("lengow.res.partner")
            external_id = binder.dict2id(record["delivery_address"], in_field=False)
            if not external_id:
                raise ValidationError(
                    _(
                        "Delivery Address not found. This Address should be defined on Lengow"
                    )
                )
            partner = binder.to_internal(external_id, unwrap=True)
            assert partner, (
                "partner_shipping_id %s should have been imported in "
                "SaleOrderImporter._import_dependencies" % external_id
            )
            return {"partner_shipping_id": partner.id}
        else:
            binding = self.options.get("binding")
            if not binding:
                parent = self.backend_record.get_marketplace_map(
                    record["marketplace"], record["parent_country_iso_a2"]
                ).partner_id
                return {"partner_shipping_id": parent.id}

    @mapping
    def billing_address(self, record):
        if record["billing_address"]:
            binder = self.binder_for("lengow.res.partner")
            external_id = binder.dict2id(record["billing_address"], in_field=False)
            partner = binder.to_internal(external_id, unwrap=True)
            assert partner, (
                "partner_id %s should have been imported in "
                "SaleOrderImporter._import_dependencies" % external_id
            )
            if not partner.active:
                raise ValidationError(
                    _(
                        "The partner %(name)s, with id:%(id)s is archived, please, enable it"
                    )
                    % {"name": partner.name, "id": partner.id}
                )
            partner_return = {"partner_invoice_id": partner.id}
            if partner.parent_id:
                partner_return["partner_id"] = partner.parent_id.id
            else:
                partner_return["partner_id"] = partner.id
            return partner_return
        else:
            binding = self.options.get("binding")
            if not binding:
                country = record.get("parent_country_iso_a2")
                if not country:
                    if record.get("marketplace_country_iso2"):
                        country = record.get("marketplace_country_iso2")
                    else:
                        raise ValidationError(
                            _(
                                "The order don't has billing address "
                                "and parent country iso a2 is empty"
                            )
                        )
                partner = self.backend_record.get_marketplace_map(
                    record["marketplace"], country
                ).partner_id
                return {"partner_invoice_id": partner.id, "partner_id": partner.id}

    @only_create
    @mapping
    def order_date(self, record):
        return {
            "date_order": record["marketplace_order_date"],
            # "confirmation_date": record["marketplace_order_date"],
            "validity_date": record["marketplace_order_date"],
        }

    @only_create
    @mapping
    def team_id(self, record):
        return {"team_id": None}

    @only_create
    @mapping
    def user_id(self, record):
        return {"user_id": None}

    @mapping
    def lengow_status(self, record):
        return {"lengow_status": record["lengow_status"]}

    @mapping
    def marketplace_status(self, record):
        return {"marketplace_status": record["marketplace_status"]}

    @mapping
    def marketplace_order_id(self, record):
        return {"client_order_ref": record["marketplace_order_id"]}