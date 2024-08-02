# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def check_consistency_report_values(self):
        for rec in self:
            if rec.partner_id.service_intermediary:
                if not rec.partner_id.service_report_config_id:
                    raise ValidationError(
                        _("The service intermediary has no service report configuration.")
                    )
                allowed_products = rec.partner_id.service_report_config_id.service_type_ids.mapped("product_ids")
                order_products = rec.order_line.mapped("product_id")
                inconsistent_products = order_products.filtered(lambda p: p not in allowed_products)
                if inconsistent_products:
                    inconsistent_product_names = ', '.join(inconsistent_products.mapped('name'))
                    raise ValidationError(
                        _(
                            "The following products are not included in the allowed "
                            "service types for this service intermediary: %s"
                        ) % inconsistent_product_names
                    )

    def get_service_typology_name(self):
        typology_name = False
        if self.partner_id.service_intermediary:
            typology_name = (
                self.partner_id.service_report_config_id.service_typology_ids.filtered(
                    lambda x: x.key == self.service_key
                    and x.transfer_reason == self.service_transfer_reason
                ).name
            )
        return typology_name

    def get_service_type_products(self, type):
        products = []
        if self.partner_id.service_intermediary:
            products = self.partner_id.service_report_config_id.service_type_ids.filtered(
                lambda x: x.type == type
            ).product_ids
        return products

    def get_service_type_quantity(self, type):
        quantity = 0
        if self.partner_id.service_intermediary:
            # TODO: Plantejar si utilitzar el type com selection es bona opcio (no es gens generic)
            products = self.get_service_type_products(type)
            quantity = sum(
                self.order_line.filtered(lambda x: x.product_id in products).mapped(
                    "product_uom_qty"
                )
            )
        return quantity

    def get_service_type_subtotal(self, type):
        price_subtotal = 0
        for rec in self:
            if rec.partner_id.service_intermediary:
                products = rec.get_service_type_products(type)
                price_subtotal += sum(
                    rec.order_line.filtered(lambda x: x.product_id in products).mapped(
                        "price_subtotal"
                    )
                )
        return price_subtotal

    def get_service_type_weighted_average_price(self, type):
        price = 0
        if self.partner_id.service_intermediary:
            products = self.get_service_type_products(type)
            quantity = self.get_service_type_quantity(type)
            if quantity:
                price = sum(
                    self.order_line.filtered(lambda x: x.product_id in products).mapped(
                        "price_subtotal"
                    )
                ) / quantity
        return price

    def get_service_type_amount_total(self, type):
        amount_total = 0
        for rec in self:
            if rec.partner_id.service_intermediary:
                amount_total += rec.get_service_type_quantity(type) * rec.get_service_type_weighted_average_price(type)
        return amount_total

    def get_service_return_price_subtotal(self, is_return_service):
        price_subtotal = 0
        for rec in self:
            if rec.partner_id.service_intermediary:
                if is_return_service == rec.return_service:
                    service_products = rec.get_service_type_products("service")
                    price_subtotal += sum(
                        rec.order_line.filtered(lambda x: x.product_id in service_products).mapped(
                            "price_subtotal"
                        )
                    )
        return price_subtotal

    def get_service_additional_concept(self):
        concept = ""
        if self.partner_id.service_intermediary:
            products = self.get_service_type_products("additional")
            self.partner_id.service_report_config_id.service_type_ids.filtered(
                lambda x: x.product_ids in products
            ).mapped("name")
        return " + ".join(concept)

    def get_service_total_by(self, field_name):
        total = 0
        if self.partner_id.service_intermediary and self[field_name]:
            move = self.order_line.invoice_lines.move_id
            orders = move.invoice_line_ids.sale_line_ids.order_id.filtered(
                lambda x: x[field_name] == self[field_name]
            )
            total_km = orders.get_service_type_amount_total("km")
            departure_price = orders.get_service_return_price_subtotal(False)
            return_price = orders.get_service_return_price_subtotal(True)
            additional_price = orders.get_service_type_subtotal("additional")
            wait_price = orders.get_service_type_subtotal("wait")
            total = total_km + departure_price + return_price + additional_price + wait_price
        return total
