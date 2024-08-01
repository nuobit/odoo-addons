# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # TODO: Hem d'afegir constrains per asegurarnos que el service_intermediary sempre tingui productes d'algun tipus de 'type'

    def get_service_typology_name(self):
        if self.partner_id.service_intermediary:
            # TODO: Fixarme si existeix me d'una fila amb el mateix key i transfer_reason (no hauria)
            return (
                self.partner_id.service_report_config_id.service_typology_ids.filtered(
                    lambda x: x.key == self.service_key
                    and x.transfer_reason == self.service_transfer_reason
                ).name
            )
        return False

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

    def get_service_type_price_subtotal(self, type):
        price_subtotal = 0
        if self.partner_id.service_intermediary:
            products = self.get_service_type_products(type)
            price_subtotal = sum(
                self.order_line.filtered(lambda x: x.product_id in products).mapped(
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
        if self.partner_id.service_intermediary:
            amount_total = self.get_service_type_quantity(type) * self.get_service_type_weighted_average_price(type)
        return amount_total

    def get_service_return_price_subtotal(self, is_return_service):
        price_subtotal = 0
        if self.partner_id.service_intermediary:
            if is_return_service == self.return_service:
                service_products = self.get_service_type_products("service")
                price_subtotal = sum(
                    self.order_line.filtered(lambda x: x.product_id in service_products).mapped(
                        "price_subtotal"
                    )
                )
        return price_subtotal

    def get_service_additional_concept(self):
        concept = ""
        if self.partner_id.service_intermediary:
            # TODO: Mirar que el service_type_ids no pot tenir el mateix producte en diferents categories
            products = self.get_service_type_products("additional")
            self.partner_id.service_report_config_id.service_type_ids.filtered(
                lambda x: x.product_ids in products
            ).mapped("name")
        return " + ".join(concept)

