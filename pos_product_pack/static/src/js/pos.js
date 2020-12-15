/* Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
   Eric Antones <eantones@nuobit.com>
   License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl) */

odoo.define('pos_product_pack.pos_product_pack', function (require) {
    "use strict";
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');

    models.load_fields('product.product',
        ['pack_ok', 'pack_type', 'pack_component_price', 'pack_line_ids']);

    models.load_models([{
            model: 'product.pack.line',
            fields: ['parent_product_id', 'product_id', 'quantity', 'sale_discount'],
            loaded: function (self, pack_lines) {
                self.pack_line_by_id = {};
                for (var i = 0; i < pack_lines.length; i++) {
                    var pack_line = pack_lines[i];
                    self.pack_line_by_id[pack_line.id] = pack_line
                }
            }
        }], {'after': ['product.product']}
    );

    screens.ProductScreenWidget.include({
        click_product: function (product) {
            var self = this;
            if (!product.pack_ok) {
                self._super(product);
            } else {
                if (product.pack_line_ids.length === 0) {
                    self._super(product);
                } else {
                    var order = this.pos.get_order()
                    var pack_lines = []
                    for (var i = 0; i < product.pack_line_ids.length; i++) {
                        var pack_line_id = product.pack_line_ids[i];
                        var pack_line = this.pos.pack_line_by_id[pack_line_id];
                        var subproduct = this.pos.db.get_product_by_id(pack_line.product_id[0]);
                        pack_lines.push({
                            'parent_product': product,
                            'product': subproduct,
                            'quantity': pack_line.quantity,
                            'sale_discount': pack_line.sale_discount || 0
                        })
                    }
                    if (product.pack_type === 'non_detailed') {
                        var price = 0;
                        for (var i = 0; i < pack_lines.length; i++) {
                            price += pack_lines[i].product.get_price(order.pricelist, 1) *
                                pack_lines[i].quantity * (1 - pack_lines[i].sale_discount / 100);
                        }
                        order.add_product(product, {
                            'price': price,
                        });
                    } else {
                        if (product.pack_component_price === 'detailed') {
                            order.add_product(product);
                            for (var i = 0; i < pack_lines.length; i++) {
                                var pack_line = pack_lines[i];
                                order.add_product(pack_line.product, {
                                    'quantity': pack_line.quantity,
                                    'discount': pack_line.sale_discount
                                });
                            }

                        } else if (product.pack_component_price === 'totalized') {
                            var price = 0;
                            for (var i = 0; i < pack_lines.length; i++) {
                                price += pack_lines[i].product.get_price(order.pricelist, 1) *
                                    pack_lines[i].quantity * (1 - pack_lines[i].sale_discount / 100);
                            }
                            order.add_product(product, {
                                'price': price,
                            });
                            for (var i = 0; i < pack_lines.length; i++) {
                                var pack_line = pack_lines[i];
                                order.add_product(pack_line.product, {
                                    'quantity': pack_line.quantity,
                                    'price': 0,
                                    'discount': 0
                                });
                            }
                        } else { // ignored
                            order.add_product(product);
                            for (var i = 0; i < pack_lines.length; i++) {
                                var pack_line = pack_lines[i];
                                order.add_product(pack_line.product, {
                                    'quantity': pack_line.quantity,
                                    'price': 0,
                                    'discount': 0
                                });
                            }
                        }
                    }
                }
            }
        }
    });
});