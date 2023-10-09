odoo.define("res_partner.SearchExpiredDocumentsKanban", async function (require) {
    "use strict";
    const __exports = {};
    const {KanbanController} = require("@web/views/kanban/kanban_controller");
    const {registry} = require("@web/core/registry");
    const {kanbanView} = require("@web/views/kanban/kanban_view");
    const ResPartnerKanbanController =
        (__exports.ResPartnerKanbanController = class ResPartnerKanbanController extends (
            KanbanController
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
                        view: "kanban",
                    },
                });
            }
        });
    registry.category("views").add("button_expired_documents_kanban", {
        ...kanbanView,
        Controller: ResPartnerKanbanController,
        buttonTemplate: "SearchExpiredDocuments.KanbanView.Buttons",
    });
    return __exports;
});
