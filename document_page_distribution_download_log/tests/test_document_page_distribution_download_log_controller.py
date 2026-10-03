# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.tests import HOST, HttpCase, tagged
from odoo.tools import config


@tagged("post_install", "-at_install")
class TestDocumentPageDistributionDownloadLogController(HttpCase):
    def setUp(self):
        super().setUp()
        self.download_model = self.env["document.page.history.recipient.download"]
        self.doc_user = self.env.ref("knowledge.group_document_user")
        self.group = self.env["res.groups"].create({"name": "Quality Audience HTTP"})
        users = self.env["res.users"].with_context(no_reset_password=True)
        self.alice = users.create(
            {
                "name": "Alice",
                "login": "alice_dpddl_http_test",
                "password": "alice_dpddl_http_test",
                "email": "alice.http@example.com",
                "groups_id": [(6, 0, [self.doc_user.id, self.group.id])],
            }
        )
        self.attachment = self.env["ir.attachment"].create(
            {
                "name": "procedure.pdf",
                "datas": base64.b64encode(b"%PDF-1.4 test").decode(),
            }
        )
        self.page = self.env["document.page"].create(
            {
                "name": "Procedure HTTP",
                "type": "content",
                "groups_id": [(6, 0, [self.group.id])],
                "content": '<p><a href="/web/content/%s">file</a></p>'
                % self.attachment.id,
            }
        )
        # the web editor binds files inserted in a page to the page record;
        # mirror that binding so /web/content grants read access to any
        # recipient that can read the page, not only the attachment's author
        self.attachment.write({"res_model": "document.page", "res_id": self.page.id})
        self.head = self.page.history_head
        self.page._ensure_distribution_recipients(
            self.head, self.page._get_distribution_coverage_users()
        )
        self.url = "/document_page_distribution_download_log/download/%s/%s" % (
            self.head.id,
            self.attachment.id,
        )

    def test_recipient_download_is_logged_over_http(self):
        self.authenticate("alice_dpddl_http_test", "alice_dpddl_http_test")
        before = self.download_model.search_count([])
        response = self.url_open(self.url, allow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertIn(
            "/web/content/%s" % self.attachment.id,
            response.headers.get("Location", ""),
        )
        self.assertEqual(self.download_model.search_count([]), before + 1)

    def test_recipient_download_serves_file_after_logging(self):
        self.authenticate("alice_dpddl_http_test", "alice_dpddl_http_test")
        before = self.download_model.search_count([])
        response = self.url_open(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"%PDF-1.4 test")
        self.assertEqual(self.download_model.search_count([]), before + 1)

    def test_click_is_served_and_recorded(self):
        self.authenticate("alice_dpddl_http_test", "alice_dpddl_http_test")
        before = self.download_model.search_count([])
        response = self.url_open(
            self.url, headers={"Sec-Fetch-Dest": "document"}, allow_redirects=False
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(self.download_model.search_count([]), before + 1)

    def test_navigation_in_a_frame_is_served_and_recorded(self):
        self.authenticate("alice_dpddl_http_test", "alice_dpddl_http_test")
        for destination in ("iframe", "frame", "embed", "object"):
            before = self.download_model.search_count([])
            response = self.url_open(
                self.url,
                headers={"Sec-Fetch-Dest": destination},
                allow_redirects=False,
            )
            self.assertEqual(response.status_code, 303, "Refused as %r" % destination)
            self.assertEqual(
                self.download_model.search_count([]),
                before + 1,
                "Not recorded as %r" % destination,
            )

    def test_request_with_no_destination_is_served_and_recorded(self):
        self.authenticate("alice_dpddl_http_test", "alice_dpddl_http_test")
        before = self.download_model.search_count([])
        response = self.url_open(
            self.url, headers={"Sec-Fetch-Dest": "empty"}, allow_redirects=False
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(self.download_model.search_count([]), before + 1)

    def test_address_asked_as_a_part_of_a_page_is_refused(self):
        self.authenticate("alice_dpddl_http_test", "alice_dpddl_http_test")
        for destination in (
            "image",
            "audio",
            "audioworklet",
            "fencedframe",
            "font",
            "json",
            "manifest",
            "paintworklet",
            "report",
            "script",
            "serviceworker",
            "sharedworker",
            "style",
            "text",
            "track",
            "video",
            "webidentity",
            "worker",
            "xslt",
            "unknown",
            "",
        ):
            before = self.download_model.search_count([])
            response = self.url_open(
                self.url,
                headers={"Sec-Fetch-Dest": destination},
                allow_redirects=False,
            )
            self.assertEqual(response.status_code, 404, "Served as %r" % destination)
            self.assertEqual(
                self.download_model.search_count([]),
                before,
                "Recorded as %r" % destination,
            )

    def test_address_asked_ahead_of_the_user_is_refused(self):
        self.authenticate("alice_dpddl_http_test", "alice_dpddl_http_test")
        for headers in (
            {"Sec-Purpose": "prefetch"},
            {"Sec-Purpose": "prefetch", "Sec-Fetch-Dest": "empty"},
            {"Sec-Purpose": "prefetch", "Sec-Fetch-Dest": "document"},
            {"Purpose": "prefetch"},
            {"Purpose": "prefetch", "Sec-Fetch-Dest": "empty"},
            {"Purpose": "prefetch", "Sec-Fetch-Dest": "document"},
            {"X-Purpose": "preview"},
            {"X-Purpose": "preview", "Sec-Fetch-Dest": "empty"},
            {"X-Purpose": "preview", "Sec-Fetch-Dest": "document"},
            {"X-Moz": "prefetch"},
            {"X-Moz": "prefetch", "Sec-Fetch-Dest": "empty"},
            {"X-Moz": "prefetch", "Sec-Fetch-Dest": "document"},
        ):
            before = self.download_model.search_count([])
            response = self.url_open(self.url, headers=headers, allow_redirects=False)
            self.assertEqual(response.status_code, 404, "Served with %r" % headers)
            self.assertEqual(
                self.download_model.search_count([]),
                before,
                "Recorded with %r" % headers,
            )

    def test_head_request_is_answered_without_a_row(self):
        self.authenticate("alice_dpddl_http_test", "alice_dpddl_http_test")
        before = self.download_model.search_count([])
        self.env["base"].flush()
        response = self.opener.head(
            "http://%s:%s%s" % (HOST, config["http_port"], self.url),
            timeout=10,
            allow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        self.assertIn(
            "/web/content/%s" % self.attachment.id,
            response.headers.get("Location", ""),
        )
        self.assertEqual(self.download_model.search_count([]), before)

    def test_download_of_a_user_who_is_not_a_recipient_is_served_and_logged(self):
        # a reader of the document who joins its group after the distribution
        bob = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Bob",
                    "login": "bob_dpddl_test",
                    "password": "bob_dpddl_test",
                    "email": "bob.http@example.com",
                    "groups_id": [(6, 0, [self.doc_user.id, self.group.id])],
                }
            )
        )
        self.authenticate("bob_dpddl_test", "bob_dpddl_test")
        response = self.url_open(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"%PDF-1.4 test")
        download = self.download_model.search([("user_id", "=", bob.id)])
        self.assertEqual(len(download), 1)
        self.assertEqual(download.history_id, self.head)
        self.assertEqual(download.attachment_id, self.attachment)
        self.assertFalse(download.recipient_id)

    def test_link_with_access_token_serves_a_file_the_reader_cannot_read(self):
        # a file bound to nothing: only its access token opens it to a reader
        self.attachment.write({"res_model": False, "res_id": False})
        access_token = self.attachment.generate_access_token()[0]
        self.authenticate("alice_dpddl_http_test", "alice_dpddl_http_test")
        response = self.url_open("%s?access_token=%s" % (self.url, access_token))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"%PDF-1.4 test")
        self.assertEqual(
            self.download_model.search_count([("user_id", "=", self.alice.id)]), 1
        )

    def test_link_with_wrong_access_token_returns_404(self):
        self.authenticate("alice_dpddl_http_test", "alice_dpddl_http_test")
        before = self.download_model.search_count([])
        response = self.url_open(
            "%s?access_token=wrong" % self.url, allow_redirects=False
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.download_model.search_count([]), before)

    def test_attachment_of_another_version_returns_404(self):
        other_attachment = self.env["ir.attachment"].create(
            {
                "name": "procedure-v2.pdf",
                "datas": base64.b64encode(b"%PDF-1.4 v2").decode(),
            }
        )
        self.page.write(
            {
                "content": '<p><a href="/web/content/%s">file</a></p>'
                % other_attachment.id
            }
        )
        v2 = self.page.history_head
        self.assertNotEqual(v2, self.head)
        self.authenticate("alice_dpddl_http_test", "alice_dpddl_http_test")
        before = self.download_model.search_count([])
        # a real attachment, but tracked by another version of the page
        forged_url = "/document_page_distribution_download_log/download/%s/%s" % (
            v2.id,
            self.attachment.id,
        )
        response = self.url_open(forged_url, allow_redirects=False)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.download_model.search_count([]), before)

    def test_forged_attachment_returns_404(self):
        self.authenticate("alice_dpddl_http_test", "alice_dpddl_http_test")
        before = self.download_model.search_count([])
        forged_url = "/document_page_distribution_download_log/download/%s/%s" % (
            self.head.id,
            self.attachment.id + 99999,
        )
        response = self.url_open(forged_url, allow_redirects=False)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.download_model.search_count([]), before)

    def test_version_without_document_returns_404(self):
        history = self.env["document.page.history"].create(
            {
                "name": "Version without document",
                "content": '<p><a href="/web/content/%s">file</a></p>'
                % self.attachment.id,
            }
        )
        self.authenticate("alice_dpddl_http_test", "alice_dpddl_http_test")
        before = self.download_model.search_count([])
        url = "/document_page_distribution_download_log/download/%s/%s" % (
            history.id,
            self.attachment.id,
        )
        response = self.url_open(url, allow_redirects=False)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.download_model.search_count([]), before)

    def test_download_of_deleted_attachment_returns_404(self):
        self.attachment.unlink()
        self.authenticate("alice_dpddl_http_test", "alice_dpddl_http_test")
        before = self.download_model.search_count([])
        response = self.url_open(self.url, allow_redirects=False)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.download_model.search_count([]), before)

    def test_unbound_attachment_returns_404_and_no_log(self):
        # a file uploaded outside the page editor is bound to nothing, so
        # /web/content would deny it to a non-author (403): no download
        # evidence may be written for a file that will not be served
        self.attachment.write({"res_model": False, "res_id": False})
        self.authenticate("alice_dpddl_http_test", "alice_dpddl_http_test")
        before = self.download_model.search_count([])
        response = self.url_open(self.url, allow_redirects=False)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.download_model.search_count([]), before)

    def test_new_page_editor_upload_serves_recipient_end_to_end(self):
        # real authoring flow: the editor uploads the file of a NOT-yet-saved
        # page as an orphan (res_model set, res_id=0, token-compensated); the
        # rewrite adopts it on save, so a covered recipient gets the file
        orphan = self.env["ir.attachment"].create(
            {
                "name": "authored.pdf",
                "datas": base64.b64encode(b"%PDF-1.4 authored").decode(),
                "res_model": "document.page",
                "res_id": 0,
            }
        )
        page = self.env["document.page"].create(
            {
                "name": "Authored from scratch HTTP",
                "type": "content",
                "groups_id": [(6, 0, [self.group.id])],
                "content": '<p><a href="/web/content/%s?access_token=x">f</a></p>'
                % orphan.id,
            }
        )
        self.assertEqual(orphan.res_id, page.id)
        head = page.history_head
        page._ensure_distribution_recipients(
            head, page._get_distribution_coverage_users()
        )
        self.authenticate("alice_dpddl_http_test", "alice_dpddl_http_test")
        before = self.download_model.search_count([])
        response = self.url_open(
            "/document_page_distribution_download_log/download/%s/%s"
            % (head.id, orphan.id)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"%PDF-1.4 authored")
        self.assertEqual(self.download_model.search_count([]), before + 1)

    def test_user_without_document_access_is_blocked(self):
        self.env["res.users"].with_context(no_reset_password=True).create(
            {
                "name": "Stranger",
                "login": "stranger_dpddl_http_test",
                "password": "stranger_dpddl_http_test",
                "groups_id": [(6, 0, [self.doc_user.id])],
            }
        )
        self.authenticate("stranger_dpddl_http_test", "stranger_dpddl_http_test")
        before = self.download_model.search_count([])
        response = self.url_open(self.url, allow_redirects=False)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.download_model.search_count([]), before)

    def test_user_without_document_access_is_blocked_even_with_a_token(self):
        # the token of the file does not open a document the user cannot read
        access_token = self.attachment.generate_access_token()[0]
        self.env["res.users"].with_context(no_reset_password=True).create(
            {
                "name": "Stranger",
                "login": "stranger_dpddl_test",
                "password": "stranger_dpddl_test",
                "groups_id": [(6, 0, [self.doc_user.id])],
            }
        )
        self.authenticate("stranger_dpddl_test", "stranger_dpddl_test")
        before = self.download_model.search_count([])
        response = self.url_open(
            "%s?access_token=%s" % (self.url, access_token), allow_redirects=False
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.download_model.search_count([]), before)
