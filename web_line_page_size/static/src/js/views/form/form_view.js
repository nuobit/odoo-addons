/* Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
   Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
   License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl) */

odoo.define("web_line_page_size.FormView", function (require) {
    "use strict";
    var FormView = require("web.FormView");
    FormView.include({
        _setSubViewLimit: function (attrs) {
            this._super(attrs);
            attrs.limit = 200;
        },
    });
});
