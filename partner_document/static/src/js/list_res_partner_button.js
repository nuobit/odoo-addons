odoo.define("res_partner.SearchExpiredDocumentsList", async function (require) {
    "use strict";
    const __exports = {};
    const {ListController} = require("@web/views/list/list_controller");
    const {registry} = require("@web/core/registry");
    const {listView} = require("@web/views/list/list_view");
    const ResPartnerListController =
        (__exports.ResPartnerListController = class ResPartnerListController extends (
            ListController
        ) {
            setup() {
                super.setup();
            }
            OnSearchExpiredDocumentsClick() {
                this.actionService.doAction({
                    type: "ir.actions.act_window",
                    res_model: "partner.document.expired.wizard",
                    name: "Search Expired Documents",
                    view_mode: "form",
                    view_type: "form",
                    views: [[false, "form"]],
                    target: "new",
                    res_id: false,
                    context: {
                        view: "tree",
                    },
                });
            }
        });
    registry.category("views").add("button_expired_documents_tree", {
        ...listView,
        Controller: ResPartnerListController,
        buttonTemplate: "SearchExpiredDocuments.ListView.Buttons",
    });
    return __exports;
});
