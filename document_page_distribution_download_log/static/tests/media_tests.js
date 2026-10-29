/* global QUnit */
/* Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("document_page_distribution_download_log.media_tests", function (require) {
    "use strict";

    const {DocumentWidget} = require("wysiwyg.widgets.media");
    const testUtils = require("web.test_utils");

    QUnit.module("document_page_distribution_download_log", {}, function () {
        QUnit.test(
            "a file saved with its tracking URL opens selected and keeps its link",
            async function (assert) {
                assert.expect(2);

                const parent = await testUtils.createParent({
                    mockRPC: function (route, args) {
                        if (
                            args.model === "ir.attachment" &&
                            args.method === "search_read"
                        ) {
                            return Promise.resolve([
                                {
                                    id: 7,
                                    name: "manual.pdf",
                                    mimetype: "application/pdf",
                                    image_src: false,
                                },
                            ]);
                        }
                        return this._super.apply(this, arguments);
                    },
                });
                const link = $("<a/>", {
                    class: "o_image",
                    href: "/document_page_distribution_download_log/download/3/7",
                })[0];
                const documentWidget = new DocumentWidget(parent, link, {});
                await documentWidget.appendTo($("#qunit-fixture"));

                assert.hasClass(
                    documentWidget.$('.o_existing_attachment_cell[data-id="7"]'),
                    "o_we_attachment_selected",
                    "the saved file is the selected one"
                );
                assert.strictEqual(
                    link.getAttribute("href"),
                    "/document_page_distribution_download_log/download/3/7",
                    "the link keeps its tracking URL"
                );

                parent.destroy();
            }
        );
    });
});
