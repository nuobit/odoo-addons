odoo.define(
    "pos_multi_sale_order_selection.SaleOrderManagementControlPanel",
    function (require) {
        "use strict";

        const SaleOrderManagementControlPanel = require("pos_sale.SaleOrderManagementControlPanel");
        const Registries = require("point_of_sale.Registries");

        const DimsSaleOrderManagementControlPanel = (
            OriginalSaleOrderManagementControlPanel
        ) =>
            class extends OriginalSaleOrderManagementControlPanel {
                get multipleSelectionCount() {
                    return this.orderManagementContext.multipleSelectionCount;
                }
                _getSaleOrderOriginIds(order) {
                    const sale_order_origin_ids = [];

                    for (const line of order.get_orderlines()) {
                        if (line.sale_order_origin_id) {
                            sale_order_origin_ids.push(line.sale_order_origin_id.id);
                        }
                    }
                    return sale_order_origin_ids;
                }
                _computeDomain() {
                    const domain = super._computeDomain();
                    const currentPOSOrder = this.env.pos.get_order();
                    const sale_order_origin_ids =
                        this._getSaleOrderOriginIds(currentPOSOrder);

                    if (sale_order_origin_ids.length > 0) {
                        domain.push(["id", "not in", sale_order_origin_ids]);
                    }

                    return domain;
                }
            };
        Registries.Component.extend(
            SaleOrderManagementControlPanel,
            DimsSaleOrderManagementControlPanel
        );
        return SaleOrderManagementControlPanel;
    }
);
