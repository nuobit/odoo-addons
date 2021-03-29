/* Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
   Eric Antones <eantones@nuobit.com>
   License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl) */

odoo.define("pos_data_validation.pos_data_validation", function (require) {
    "use strict";

    var core = require("web.core");
    var ActionpadWidget = require("point_of_sale.screens").ActionpadWidget;

    var _t = core._t;

    ActionpadWidget.include({
        rpc_check_data: function (config_id, lines) {
            return this._rpc({
                model: "pos.order",
                method: "check_lines",
                args: [config_id, lines],
            });
        },
        renderElement: function () {
            var self = this;
            this._super();
            this.$(".pay").off("click");

            this.$(".pay").click(function () {
                var order = self.pos.get_order();
                var has_valid_product_lot = _.every(order.orderlines.models, function (
                    line
                ) {
                    return line.has_valid_product_lot();
                });
                if (has_valid_product_lot) {
                    var prepared_lines = _.map(order.get_orderlines(), function (l) {
                        return {
                            product_id: l.product.id,
                            lot_name: _.map(l.pack_lot_lines.models, function (m) {
                                return m.attributes.lot_name;
                            }),
                            quantity: l.quantity,
                        };
                    });
                    self.rpc_check_data(self.pos.config.id, prepared_lines).then(
                        function (result) {
                            if (result) {
                                self.gui.show_popup("error", {
                                    title: _t("Error"),
                                    body: result.msg,
                                });
                            } else {
                                self.gui.show_screen("payment");
                            }
                        }
                    );
                } else {
                    self.gui.show_popup("error", {
                        title: _t("Empty Serial/Lot Number"),
                        body: _t("One or more product(s) required serial/lot number."),
                    });
                }
            });
        },
    });
});
