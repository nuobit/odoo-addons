// Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
// Eric Antones <eantones@nuobit.com>
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
odoo.define("report_json.report", function (require) {
    "use strict";

    var ActionManager = require("web.ActionManager");
    var crash_manager = require("web.crash_manager");
    var framework = require("web.framework");

    ActionManager.include({
        ir_actions_report: function (action, options) {
            var self = this;
            var cloned_action = _.clone(action);
            if (cloned_action.report_type === "json") {
                framework.blockUI();
                var report_json_url = "report/json/" + cloned_action.report_name;
                if (
                    _.isUndefined(cloned_action.data) ||
                    _.isNull(cloned_action.data) ||
                    (_.isObject(cloned_action.data) && _.isEmpty(cloned_action.data))
                ) {
                    if (cloned_action.context.active_ids) {
                        report_json_url +=
                            "/" + cloned_action.context.active_ids.join(",");
                    }
                } else {
                    report_json_url +=
                        "?options=" +
                        encodeURIComponent(JSON.stringify(cloned_action.data));
                    report_json_url +=
                        "&context=" +
                        encodeURIComponent(JSON.stringify(cloned_action.context));
                }
                self.getSession().get_file({
                    url: report_json_url,
                    data: {
                        data: JSON.stringify([
                            report_json_url,
                            cloned_action.report_type,
                        ]),
                    },
                    error: crash_manager.rpc_error.bind(crash_manager),
                    success: function () {
                        if (cloned_action && options && !cloned_action.dialog) {
                            options.on_close();
                        }
                    },
                });
                framework.unblockUI();
                return;
            }
            return self._super(action, options);
        },
    });
});
