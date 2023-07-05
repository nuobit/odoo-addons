odoo.define("pos_multi_sale_order_selection.PosContext", function (require) {
    "use strict";
    const PosContext = require("point_of_sale.PosContext");
    const {reactive} = owl;

    PosContext.orderManagement = reactive({
        ...PosContext.orderManagement,
        multipleSelectionCount: 0,
        clickedOrder: [],
    });
    return PosContext;
});
