/* Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("document_page_distribution_download_log.FileWidget", function (require) {
    "use strict";

    const {FileWidget} = require("wysiwyg.widgets.media");

    // The tracking URL of a file of a version, built by _get_tracking_url
    // (models/document_page_history.py): /<route>/<version id>/<attachment id>
    const TRACKING_URL = /^\/document_page_distribution_download_log\/download\/\d+\/(\d+)/;

    FileWidget.include({
        /**
         * The editor reads the attachment of a selected file only from a
         * /web/content address, inside start itself, and Odoo 14 offers no
         * hook for that reading. A file saved in a version links to its
         * tracking URL, so while start runs the link shows the editor the
         * /web/content address of the same attachment, and gets its own
         * address back as soon as start returns: the reading is synchronous
         * and the saved link never changes.
         *
         * @override
         */
        start: function () {
            const href = this.$media.attr("href");
            const tracked =
                this.$media.is("a.o_image") && href && href.match(TRACKING_URL);
            if (!tracked) {
                return this._super.apply(this, arguments);
            }
            this.$media.attr("href", "/web/content/" + tracked[1]);
            try {
                return this._super.apply(this, arguments);
            } finally {
                this.$media.attr("href", href);
            }
        },
    });
});
