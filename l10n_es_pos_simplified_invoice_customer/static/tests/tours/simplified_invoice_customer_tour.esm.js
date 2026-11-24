/** @odoo-module **/
/* Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import * as PaymentScreen from "@point_of_sale/../tests/tours/helpers/PaymentScreenTourMethods";
import * as ProductScreen from "@point_of_sale/../tests/tours/helpers/ProductScreenTourMethods";
import * as ReceiptScreen from "@point_of_sale/../tests/tours/helpers/ReceiptScreenTourMethods";
import {registry} from "@web/core/registry";

function payOrder(customer) {
    return [
        ProductScreen.addOrderline("Desk Pad", "1"),
        ProductScreen.clickPartnerButton(),
        ProductScreen.clickCustomer(customer),
        ProductScreen.clickPayButton(),
        PaymentScreen.clickPaymentMethod("Bank"),
    ].flat();
}

// The ticket prints nothing of the customer's block: no «Customer:», no name
// and no address (its tax ID is a line of the same block)
function printsNoCustomer(name, street) {
    return [
        {
            content: `the ticket prints no customer: neither ${name} nor its address`,
            trigger: `.receipt-screen .pos-receipt:not(:contains('Customer:')):not(:contains('${name}')):not(:contains('${street}'))`,
            isCheck: true,
        },
    ];
}

registry
    .category("web_tour.tours")
    .add("l10n_es_pos_simplified_invoice_customer_tour", {
        test: true,
        steps: () =>
            [
                ProductScreen.confirmOpeningPopup(),

                // A simplified invoice for a customer without a tax ID
                payOrder("Customer Without Tax ID"),
                PaymentScreen.clickValidate(),
                {
                    content: "the ticket is a simplified invoice",
                    trigger: ".receipt-screen .simplified-invoice-number",
                    isCheck: true,
                },
                printsNoCustomer("Customer Without Tax ID", "Main Street 1"),
                ReceiptScreen.clickNextOrder(),

                // A simplified invoice for a customer not subject to tax
                payOrder("Customer Not Subject To Tax"),
                PaymentScreen.clickValidate(),
                {
                    content: "the ticket is a simplified invoice",
                    trigger: ".receipt-screen .simplified-invoice-number",
                    isCheck: true,
                },
                printsNoCustomer("Customer Not Subject To Tax", "New Street 1"),
                ReceiptScreen.clickNextOrder(),

                // A simplified invoice for a customer with a tax ID
                payOrder("Customer With Tax ID"),
                PaymentScreen.clickValidate(),
                {
                    content: "the ticket is a simplified invoice",
                    trigger: ".receipt-screen .simplified-invoice-number",
                    isCheck: true,
                },
                {
                    content: "the ticket prints the customer's name",
                    trigger:
                        ".receipt-screen .pos-receipt-contact:contains('Customer: Customer With Tax ID')",
                    isCheck: true,
                },
                {
                    content: "the ticket prints the customer's tax ID",
                    trigger:
                        ".receipt-screen .pos-receipt-contact:contains('ES12345678Z')",
                    isCheck: true,
                },
                {
                    content: "the ticket prints the customer's address",
                    trigger:
                        ".receipt-screen .pos-receipt-contact:contains('New Street 2')",
                    isCheck: true,
                },
                ReceiptScreen.clickNextOrder(),

                // An invoice for a customer without a tax ID: as before
                payOrder("Customer Without Tax ID"),
                PaymentScreen.clickInvoiceButton(),
                PaymentScreen.clickValidate(),
                {
                    content: "the ticket prints the customer",
                    trigger:
                        ".receipt-screen .pos-receipt-contact:contains('Customer: Customer Without Tax ID')",
                    isCheck: true,
                },
                {
                    content: "the ticket is not a simplified invoice",
                    trigger: ".receipt-screen:not(:has(.simplified-invoice-number))",
                    isCheck: true,
                },
            ].flat(),
    });
