/* Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
   Eric Antones <eantones@nuobit.com>
   License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl) */

odoo.define('pos_product_service_time.pos_product_service_time', function (require) {
    "use strict";
    var models = require('point_of_sale.models');

    models.load_fields('product.product', ['type', 'service_time']);

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function (attr, options) {
            _super_orderline.initialize.call(this, attr, options);
        },
        get_service_time_minutes_str: function () {
            var service_time_hour = this.product.service_time;
            if (this.product.type === 'service' && service_time_hour > 0) {
                return (service_time_hour * 60).toFixed(0) + "'";
            }
            return undefined;
        }
    });
});