odoo.define("pos_multi_sale_order_selection.SaleOrderRow", function (require) {
    "use strict";

    const SaleOrderRow = require("pos_sale.SaleOrderRow");
    const Registries = require("point_of_sale.Registries");
    const contexts = require("point_of_sale.PosContext");

    const {useState} = owl;

    const DimsSaleOrderRow = (OriginalSaleOrderRow) =>
        class extends OriginalSaleOrderRow {
            setup() {
                super.setup();
                this.orderManagementContext = useState(contexts.orderManagement);
            }

            get highlighted() {
                const baseHighlighted = super.highlighted;

                const clickedOrders = this.orderManagementContext.clickedOrder;
                const orderExistsInClickedOrders = clickedOrders.find(
                    (clickedOrder) => clickedOrder.order.id === this.order.id
                );
                return baseHighlighted || Boolean(orderExistsInClickedOrders);
            }
        };
    Registries.Component.extend(SaleOrderRow, DimsSaleOrderRow);
    return SaleOrderRow;
});
