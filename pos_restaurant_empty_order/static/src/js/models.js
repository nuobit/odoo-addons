odoo.define("pos_restaurant_empty_order.models", function (require) {
    "use strict";

    require("pos_restaurant.models");
    const {PosGlobalState} = require("point_of_sale.models");
    const Registries = require("point_of_sale.Registries");

    const PosRestaurantCustomerPosGlobalState = (PosRestaurantPosGlobalState) =>
        class extends PosRestaurantPosGlobalState {
            getCustomerCount(tableId) {
                const tableOrders = this.getTableOrders(tableId).filter(
                    (order) => !order.finalized
                );
                return tableOrders.some((order) => order.orderlines.length > 0)
                    ? tableOrders.reduce(
                          (accumulatedCount, order) =>
                              accumulatedCount + order.getCustomerCount(),
                          0
                      )
                    : 0;
            }
        };

    Registries.Model.extend(PosGlobalState, PosRestaurantCustomerPosGlobalState);
});
