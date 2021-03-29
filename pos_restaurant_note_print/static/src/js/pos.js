/* Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
   Eric Antones <eantones@nuobit.com>
   License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl) */

odoo.define("pos_restaurant_note_print.pos_restaurant_note_print", function (require) {
    "use strict";

    var module = require("point_of_sale.models");

    var _super_orderline = module.Orderline.prototype;
    module.Orderline = module.Orderline.extend({
        export_for_printing: function () {
            var json = _super_orderline.export_for_printing.apply(this, arguments);
            json.note = this.get_note();
            return json;
        },
    });
});
