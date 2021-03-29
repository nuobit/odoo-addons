/* Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
   Eric Antones <eantones@nuobit.com>
   License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl) */

odoo.define("pos_product_pack.pos_product_pack", function (require) {
    "use strict";
    var screens = require("point_of_sale.screens");
    var models = require("point_of_sale.models");
    var core = require("web.core");
    var _t = core._t;

    models.load_fields("product.product", [
        "pack_ok",
        "pack_type",
        "pack_component_price",
        "pack_line_ids",
        "used_in_pack_line_ids",
    ]);

    models.load_models(
        [
            {
                model: "product.pack.line",
                fields: [
                    "parent_product_id",
                    "product_id",
                    "quantity",
                    "sale_discount",
                ],
                loaded: function (self, pack_lines) {
                    self.pack_line_by_id = {};
                    self.pack_line_by_parent_product = {};
                    for (var i = 0; i < pack_lines.length; i++) {
                        var pack_line = pack_lines[i];
                        self.pack_line_by_id[pack_line.id] = pack_line;
                        var parent_product_id = pack_line.parent_product_id[0];
                        var product_id = pack_line.product_id[0];
                        if (
                            self.pack_line_by_parent_product[parent_product_id] ===
                            undefined
                        ) {
                            self.pack_line_by_parent_product[parent_product_id] = {};
                        }
                        self.pack_line_by_parent_product[parent_product_id][
                            product_id
                        ] = pack_line;
                    }
                },
            },
        ],
        {after: ["product.product"]}
    );

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function (attr, options) {
            _super_orderline.initialize.call(this, attr, options);
        },
        can_be_merged_with: function (orderline) {
            var res = _super_orderline.can_be_merged_with.call(this, orderline);
            return res;
        },
        set_quantity: function (quantity) {
            /* eslint-disable max-depth */
            this.order.assert_editable();
            if (this.product.pack_ok) {
                var to_remove = [];
                var orderlines = this.order.get_orderlines();
                for (var i = 0; i < orderlines.length; i++) {
                    var orderline = orderlines[i];
                    if (orderline.product.id !== this.product.id) {
                        var pack_line = this.pos.pack_line_by_parent_product[
                            this.product.id
                        ][orderline.product.id];
                        if (pack_line) {
                            if (quantity === "remove") {
                                to_remove.push(orderline);
                            } else {
                                orderline.set_quantity(
                                    pack_line.quantity * quantity,
                                    true
                                );
                            }
                        }
                    }
                }
                for (var j = 0; j < to_remove.length; j++) {
                    this.order.remove_orderline(to_remove[j]);
                }
            }
            return _super_orderline.set_quantity.apply(this, arguments);
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (attr, options) {
            _super_order.initialize.call(this, attr, options);
        },
        get_orderline_by_product: function (product) {
            var found = [];
            var orderlines = this.get_orderlines();
            for (var i = 0; i < orderlines.length; i++) {
                var orderline = orderlines[i];
                if (orderline.product.id === product.id) {
                    found.push(orderline);
                }
            }
            return (found.length && found) || undefined;
        },
    });

    screens.ProductScreenWidget.include({
        click_product: function (product) {
            var self = this;
            if (!product.pack_ok) {
                self._super(product);
            } else if (product.pack_line_ids.length === 0) {
                self._super(product);
            } else {
                var order = this.pos.get_order();
                var orderline = order.get_orderline_by_product(product);
                if (orderline) {
                    throw new Error(
                        _t(
                            "Only one pack of the same type can be added, modify the existing one"
                        )
                    );
                }
                var pack_lines = [];
                var pack_line = {};
                for (var i = 0; i < product.pack_line_ids.length; i++) {
                    var pack_line_id = product.pack_line_ids[i];
                    pack_line = this.pos.pack_line_by_id[pack_line_id];
                    var subproduct = this.pos.db.get_product_by_id(
                        pack_line.product_id[0]
                    );
                    pack_lines.push({
                        parent_product: product,
                        product: subproduct,
                        quantity: pack_line.quantity,
                        sale_discount: pack_line.sale_discount || 0,
                    });
                }
                var price = 0;
                if (product.pack_type === "non_detailed") {
                    for (var j = 0; j < pack_lines.length; j++) {
                        price +=
                            pack_lines[j].product.get_price(order.pricelist, 1) *
                            pack_lines[j].quantity *
                            (1 - pack_lines[j].sale_discount / 100);
                    }
                    order.add_product(product, {
                        price: price,
                    });
                } else if (product.pack_component_price === "detailed") {
                    order.add_product(product);
                    for (var k = 0; k < pack_lines.length; k++) {
                        pack_line = pack_lines[k];
                        order.add_product(pack_line.product, {
                            quantity: pack_line.quantity,
                            discount: pack_line.sale_discount,
                        });
                    }
                } else if (product.pack_component_price === "totalized") {
                    for (var r = 0; r < pack_lines.length; r++) {
                        price +=
                            pack_lines[r].product.get_price(order.pricelist, 1) *
                            pack_lines[r].quantity *
                            (1 - pack_lines[r].sale_discount / 100);
                    }
                    order.add_product(product, {
                        price: price,
                    });
                    for (var s = 0; s < pack_lines.length; s++) {
                        pack_line = pack_lines[s];
                        order.add_product(pack_line.product, {
                            quantity: pack_line.quantity,
                            price: 0,
                            discount: 0,
                        });
                    }
                } else {
                    // Ignored
                    order.add_product(product);
                    for (var t = 0; t < pack_lines.length; t++) {
                        pack_line = pack_lines[t];
                        order.add_product(pack_line.product, {
                            quantity: pack_line.quantity,
                            price: 0,
                            discount: 0,
                        });
                    }
                }
            }
        },
    });
});
