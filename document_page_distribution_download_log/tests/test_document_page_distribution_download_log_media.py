# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestDocumentPageDistributionDownloadLogMedia(HttpCase):
    def test_js(self):
        self.browser_js(
            "/web/tests?debug=assets&module=document_page_distribution_download_log",
            "",
            login="admin",
        )
