# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def get_service_typology_name(self):
        typology_name = False
        if self.partner_id.service_intermediary:
            typology_name = (
                self.partner_id.service_report_config_id.typology_ids.filtered(
                    lambda x: x.key == self.service_key
                    and x.transfer_reason == self.service_transfer_reason
                ).name
            )
        return typology_name

    def get_service_type_products(self, svc_type):
        products = []
        if self.partner_id.service_intermediary:
            products = self.partner_id.service_report_config_id.type_ids.filtered(
                lambda x: x.type == svc_type
            ).product_ids
        return products

    def get_service_type_quantity(self, svc_type):
        quantity = 0
        if self.partner_id.service_intermediary:
            products = self.get_service_type_products(svc_type)
            quantity = sum(
                self.order_line.filtered(lambda x: x.product_id in products).mapped(
                    "product_uom_qty"
                )
            )
        return quantity

    def get_service_type_subtotal(self, svc_type):
        price_subtotal = 0
        for rec in self:
            if rec.partner_id.service_intermediary:
                products = rec.get_service_type_products(svc_type)
                price_subtotal += sum(
                    rec.order_line.filtered(lambda x: x.product_id in products).mapped(
                        "price_subtotal"
                    )
                )
        return price_subtotal

    def get_service_type_weighted_average_price(self, svc_type):
        price = 0
        if self.partner_id.service_intermediary:
            products = self.get_service_type_products(svc_type)
            quantity = self.get_service_type_quantity(svc_type)
            if quantity:
                price = (
                    sum(
                        self.order_line.filtered(
                            lambda x: x.product_id in products
                        ).mapped("price_subtotal")
                    )
                    / quantity
                )
        return price

    def get_service_type_amount_total(self, svc_type):
        amount_total = 0
        for rec in self:
            if rec.partner_id.service_intermediary:
                amount_total += rec.get_service_type_quantity(
                    svc_type
                ) * rec.get_service_type_weighted_average_price(svc_type)
        return amount_total

    def get_service_return_price_subtotal(self, is_return_service):
        price_subtotal = 0
        for rec in self:
            if rec.partner_id.service_intermediary:
                if is_return_service == rec.return_service:
                    service_products = rec.get_service_type_products("service")
                    price_subtotal += sum(
                        rec.order_line.filtered(
                            lambda x: x.product_id in service_products
                        ).mapped("price_subtotal")
                    )
        return price_subtotal

    def get_service_additional_concept(self):
        concept = ""
        if self.partner_id.service_intermediary:
            concept = self.partner_id.service_report_config_id.type_ids.filtered(
                lambda x: x.type == "additional"
                and self.order_line.product_id & x.product_ids
            ).mapped("name")
        return " + ".join(concept)

    def get_service_total_by(self, field_name):
        total = 0
        if self.partner_id.service_intermediary and self[field_name]:
            move = self.order_line.invoice_lines.move_id
            orders = move.invoice_line_ids.sale_line_ids.order_id.filtered(
                lambda x: x[field_name] == self[field_name]
            )
            total = (
                orders.get_service_type_amount_total("km")
                + orders.get_service_return_price_subtotal(False)
                + orders.get_service_return_price_subtotal(True)
                + orders.get_service_type_subtotal("additional")
                + orders.get_service_type_subtotal("wait")
            )
        return total
