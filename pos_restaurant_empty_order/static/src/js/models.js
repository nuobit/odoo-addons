odoo.define("pos_restaurant_empty_order.models", function (require) {
    "use strict";

    const OrderWidget = require("point_of_sale.OrderWidget");
    const Registries = require("point_of_sale.Registries");
    const {useExternalListener, onWillDestroy} = owl;

    const PosRestaurantEmptyOrderWidget = (OriginalOrderWidget) =>
        class extends OriginalOrderWidget {
            setup() {
                super.setup();
                useExternalListener(window, "beforeunload", this._onBeforeUnload);
                onWillDestroy(this.onWillDestroy);
            }
            _onBeforeUnload() {
                this.removeOrdersWithoutLines();
            }
            onWillDestroy() {
                this.removeOrdersWithoutLines();
            }
            removeOrdersWithoutLines() {
                this.env.pos.removeOrder(this.env.pos.get_order());
                delete this.env.pos.selectedOrder;
            }
        };

    Registries.Component.extend(OrderWidget, PosRestaurantEmptyOrderWidget);

    return OrderWidget;
});
