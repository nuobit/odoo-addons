odoo.define("pos_restaurant_force_table_guests.FloorScreen", function (require) {
    "use strict";

    const FloorScreen = require("pos_restaurant.FloorScreen");
    const {isConnectionError} = require("point_of_sale.utils");
    const {patch} = require("web.utils");

    patch(FloorScreen.prototype, "pos_restaurant_force_table_guests.FloorScreen", {
        async onSelectTable(table) {
            if (this.state.isEditMode) {
                this.state.selectedTableId = table.id;
            } else {
                try {
                    let guestCount = 0;
                    let currentOrder = this.env.pos
                        .getTableOrders(table.id)
                        .find((order) => !order.finalized);
                    const nGuests = currentOrder ? currentOrder.getCustomerCount() : 0;
                    if (nGuests <= 0) {
                        const {confirmed, payload: inputNumber} = await this.showPopup(
                            "NumberPopup",
                            {
                                startingValue: nGuests.toString(),
                                cheap: true,
                                title: this.env._t("Guests ?"),
                                isInputSelected: true,
                            }
                        );

                        if (confirmed) {
                            guestCount = parseInt(inputNumber, 10) || 1;
                        } else {
                            return;
                        }
                    }
                    if (this.env.pos.orderToTransfer) {
                        await this.env.pos.transferTable(table);
                    } else {
                        await this.env.pos.setTable(table);
                    }
                    if (nGuests <= 0) {
                        currentOrder = this.env.pos.get_order();
                        currentOrder.setCustomerCount(guestCount);
                    }
                } catch (error) {
                    if (isConnectionError(error)) {
                        await this.showPopup("OfflineErrorPopup", {
                            title: this.env._t("Offline"),
                            body: this.env._t("Unable to fetch orders"),
                        });
                    } else {
                        throw error;
                    }
                }
                const order = this.env.pos.get_order();
                this.showScreen(order.get_screen_data().name);
            }
        },
    });

    return FloorScreen;
});
