/** @odoo-module **/
/* Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {afterNextRender, start, startServer} from "@mail/../tests/helpers/test_utils";
import {patchWithCleanup} from "@web/../tests/helpers/utils";
import {session} from "@web/session";

const {QUnit} = window;

QUnit.module("mail_app_icon_flat", {
    beforeEach() {
        patchWithCleanup(session, {
            flat_icon_urls: {
                "/crm/static/description/icon.png":
                    "/web_app_icon_flat/static/img/crm/icon.png",
            },
        });
    },
});

QUnit.test("activity menu shows the flat icon of an Odoo app", async function (assert) {
    assert.expect(1);

    const {click} = await start({
        async mockRPC(route, args) {
            if (args.method === "systray_get_activities") {
                return [
                    {
                        actions: [{icon: "fa-clock-o", name: "Summary"}],
                        icon: "/crm/static/description/icon.png",
                        id: "crm.lead",
                        model: "crm.lead",
                        name: "Lead/Opportunity",
                        overdue_count: 0,
                        planned_count: 0,
                        today_count: 1,
                        total_count: 1,
                        type: "activity",
                    },
                ];
            }
        },
    });
    await click('.dropdown-toggle[title="Activities"]');
    assert.strictEqual(
        document.querySelector(".o_ActivityMenuView_activityGroupIconContainer img")
            .dataset.src,
        "/web_app_icon_flat/static/img/crm/icon.png",
        "should show the flat icon of the app"
    );
});

QUnit.test("activity menu keeps the icon of another module", async function (assert) {
    assert.expect(1);

    const {click} = await start({
        async mockRPC(route, args) {
            if (args.method === "systray_get_activities") {
                return [
                    {
                        actions: [{icon: "fa-clock-o", name: "Summary"}],
                        icon: "/web_app_icon_flat/static/description/icon.png",
                        id: "res.partner",
                        model: "res.partner",
                        name: "Contact",
                        overdue_count: 0,
                        planned_count: 0,
                        today_count: 1,
                        total_count: 1,
                        type: "activity",
                    },
                ];
            }
        },
    });
    await click('.dropdown-toggle[title="Activities"]');
    assert.strictEqual(
        document.querySelector(".o_ActivityMenuView_activityGroupIconContainer img")
            .dataset.src,
        "/web_app_icon_flat/static/description/icon.png",
        "should keep the icon of the module"
    );
});

QUnit.test(
    "messaging menu shows the flat icon of an Odoo app",
    async function (assert) {
        assert.expect(1);

        const pyEnv = await startServer();
        const resPartnerId1 = pyEnv["res.partner"].create({});
        const mailMessageId1 = pyEnv["mail.message"].create({
            model: "res.partner",
            needaction: true,
            needaction_partner_ids: [pyEnv.currentPartnerId],
            res_id: resPartnerId1,
        });
        pyEnv["mail.notification"].create({
            mail_message_id: mailMessageId1,
            notification_status: "sent",
            notification_type: "inbox",
            res_partner_id: pyEnv.currentPartnerId,
        });
        const {afterEvent, messaging} = await start({
            async mockRPC(route, args, performRPC) {
                if (route === "/mail/inbox/messages") {
                    // The mock server sends no module icon.
                    const messages = await performRPC(route, args);
                    return messages.map((message) => ({
                        ...message,
                        module_icon: "/crm/static/description/icon.png",
                    }));
                }
            },
        });
        await afterNextRender(() =>
            afterEvent({
                eventName: "o-thread-cache-loaded-messages",
                func: () => document.querySelector(".o_MessagingMenu_toggler").click(),
                message: "should wait until inbox loaded initial needaction messages",
                predicate: ({threadCache}) => {
                    return threadCache.thread === messaging.inbox.thread;
                },
            })
        );
        assert.strictEqual(
            document.querySelector(".o_ThreadNeedactionPreview_image").dataset.src,
            "/web_app_icon_flat/static/img/crm/icon.png",
            "should show the flat icon of the app"
        );
    }
);

QUnit.test("messaging menu keeps the icon of another module", async function (assert) {
    assert.expect(1);

    const pyEnv = await startServer();
    const resPartnerId1 = pyEnv["res.partner"].create({});
    const mailMessageId1 = pyEnv["mail.message"].create({
        model: "res.partner",
        needaction: true,
        needaction_partner_ids: [pyEnv.currentPartnerId],
        res_id: resPartnerId1,
    });
    pyEnv["mail.notification"].create({
        mail_message_id: mailMessageId1,
        notification_status: "sent",
        notification_type: "inbox",
        res_partner_id: pyEnv.currentPartnerId,
    });
    const {afterEvent, messaging} = await start({
        async mockRPC(route, args, performRPC) {
            if (route === "/mail/inbox/messages") {
                // The mock server sends no module icon.
                const messages = await performRPC(route, args);
                return messages.map((message) => ({
                    ...message,
                    module_icon: "/web_app_icon_flat/static/description/icon.png",
                }));
            }
        },
    });
    await afterNextRender(() =>
        afterEvent({
            eventName: "o-thread-cache-loaded-messages",
            func: () => document.querySelector(".o_MessagingMenu_toggler").click(),
            message: "should wait until inbox loaded initial needaction messages",
            predicate: ({threadCache}) => {
                return threadCache.thread === messaging.inbox.thread;
            },
        })
    );
    assert.strictEqual(
        document.querySelector(".o_ThreadNeedactionPreview_image").dataset.src,
        "/web_app_icon_flat/static/description/icon.png",
        "should keep the icon of the module"
    );
});

QUnit.test("message without module icon", async function (assert) {
    assert.expect(1);

    const {messaging} = await start();
    const message = messaging.models.Message.convertData({
        id: 100,
        model: "res.partner",
        res_id: 20,
    });
    assert.notOk("moduleIcon" in message.originThread);
});
