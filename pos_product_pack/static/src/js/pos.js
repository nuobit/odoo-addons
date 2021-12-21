/* Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
   Eric Antones <eantones@nuobit.com>
   License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl) */

odoo.define("pos_product_pack.pos_product_pack", function (require) {
    "use strict";
    const {patch} = require("web.utils");
    const ProductScreen = require("point_of_sale.ProductScreen");
    const NumberBuffer = require("point_of_sale.NumberBuffer");

    const models = require("point_of_sale.models");
    const core = require("web.core");
    const _t = core._t;

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
                    for (let i = 0; i < pack_lines.length; i++) {
                        const pack_line = pack_lines[i];
                        self.pack_line_by_id[pack_line.id] = pack_line;
                        const parent_product_id = pack_line.parent_product_id[0];
                        const product_id = pack_line.product_id[0];
                        if (
                            self.pack_line_by_parent_product[parent_product_id] ===
                            undefined
                        ) {
                            self.pack_line_by_parent_product[parent_product_id] = {};
                            self.pack_line_by_parent_product[parent_product_id][
                                product_id
                            ] = pack_line;
                        }
                    }
                },
            },
        ],
        {after: ["product.product"]}
    );

    const _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function (attr, options) {
            _super_orderline.initialize.call(this, attr, options);
        },
        can_be_merged_with: function (orderline) {
            const res = _super_orderline.can_be_merged_with.call(this, orderline);
            return res;
        },
        set_quantity: function (quantity) {
            /* eslint-disable max-depth */
            this.order.assert_editable();
            if (this.product.pack_ok) {
                const to_remove = [];
                const orderlines = this.order.get_orderlines();
                for (let i = 0; i < orderlines.length; i++) {
                    const orderline = orderlines[i];
                    if (orderline.product.id !== this.product.id) {
                        const pack_line = this.pos.pack_line_by_parent_product[
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
                for (let j = 0; j < to_remove.length; j++) {
                    this.order.remove_orderline(to_remove[j]);
                }
            }
            return _super_orderline.set_quantity.apply(this, arguments);
        },
    });

    const _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (attr, options) {
            _super_order.initialize.call(this, attr, options);
        },
        get_orderline_by_product: function (product) {
            const found = [];
            const orderlines = this.get_orderlines();
            for (let i = 0; i < orderlines.length; i++) {
                const orderline = orderlines[i];
                if (orderline.product.id === product.id) {
                    found.push(orderline);
                }
            }
            return (found.length && found) || undefined;
        },
    });

    patch(ProductScreen, "pos_product_pack.pos_product_pack", {
        _clickProduct: async function (event) {
            const self = this;
            const product = event.detail;
            if (!product.pack_ok) {
                self._super(event);
            } else if (product.pack_line_ids.length === 0) {
                self._super(event);
            } else {
                const options = await this._getAddProductOptions(product);
                // Do not add product if options is undefined.
                if (!options) return;
                const order = self.currentOrder;
                const orderline = order.get_orderline_by_product(product);
                if (orderline) {
                    throw new Error(
                        _t(
                            "Only one pack of the same type can be added, modify the existing one"
                        )
                    );
                }
                const pack_lines = [];
                let pack_line = {};
                for (let i = 0; i < product.pack_line_ids.length; i++) {
                    const pack_line_id = product.pack_line_ids[i];
                    pack_line = this.env.pos.pack_line_by_id[pack_line_id];
                    const subproduct = this.env.pos.db.get_product_by_id(
                        pack_line.product_id[0]
                    );
                    pack_lines.push({
                        parent_product: product,
                        product: subproduct,
                        quantity: pack_line.quantity,
                        sale_discount: pack_line.sale_discount || 0,
                    });
                }
                let price = 0;
                if (product.pack_type === "non_detailed") {
                    for (let j = 0; j < pack_lines.length; j++) {
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
                    for (let k = 0; k < pack_lines.length; k++) {
                        pack_line = pack_lines[k];
                        order.add_product(pack_line.product, {
                            quantity: pack_line.quantity,
                            discount: pack_line.sale_discount,
                        });
                    }
                } else if (product.pack_component_price === "totalized") {
                    for (let r = 0; r < pack_lines.length; r++) {
                        price +=
                            pack_lines[r].product.get_price(order.pricelist, 1) *
                            pack_lines[r].quantity *
                            (1 - pack_lines[r].sale_discount / 100);
                    }
                    order.add_product(product, {
                        price: price,
                    });
                    for (let s = 0; s < pack_lines.length; s++) {
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
                    for (let t = 0; t < pack_lines.length; t++) {
                        pack_line = pack_lines[t];
                        order.add_product(pack_line.product, {
                            quantity: pack_line.quantity,
                            price: 0,
                            discount: 0,
                        });
                    }
                }
                NumberBuffer.reset();
            }
        },
    });
});
