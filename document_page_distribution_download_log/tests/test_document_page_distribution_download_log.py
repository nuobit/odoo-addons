# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from datetime import datetime

from freezegun import freeze_time

from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import SavepointCase


class TestDocumentPageDistributionDownloadLog(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.doc_user = cls.env.ref("knowledge.group_document_user")
        cls.group = cls.env["res.groups"].create({"name": "Quality Audience"})
        users = cls.env["res.users"].with_context(no_reset_password=True)
        cls.alice = users.create(
            {
                "name": "Alice",
                "login": "alice_dpddl",
                "email": "alice@example.com",
                "groups_id": [(6, 0, [cls.doc_user.id, cls.group.id])],
            }
        )
        cls.attachment = cls.env["ir.attachment"].create(
            {
                "name": "procedure.pdf",
                "datas": base64.b64encode(b"%PDF-1.4 test").decode(),
            }
        )
        cls.page = cls.env["document.page"].create(
            {
                "name": "Procedure",
                "type": "content",
                "groups_id": [(6, 0, [cls.group.id])],
                "content": cls._doc_link(cls.attachment.id),
            }
        )
        cls.head = cls.page.history_head
        cls.page._ensure_distribution_recipients(
            cls.head, cls.page._get_distribution_coverage_users()
        )

    @classmethod
    def _doc_link(cls, attachment_id, count=1):
        return "".join(
            '<p><a href="/web/content/%s">file %s</a></p>' % (attachment_id, i)
            for i in range(count)
        )

    def _recipient(self, history, user):
        return self.env["document.page.history.recipient"].search(
            [
                ("history_id", "=", history.id),
                ("partner_id", "=", user.partner_id.id),
            ]
        )

    def test_link_is_rewritten_with_history_id(self):
        route = "/document_page_distribution_download_log/download/%s/%s" % (
            self.head.id,
            self.attachment.id,
        )
        self.assertIn(route, self.head.content)
        self.assertNotIn('"/web/content/%s"' % self.attachment.id, self.head.content)

    def test_more_than_one_document_link_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.env["document.page"].create(
                {
                    "name": "Two links",
                    "type": "content",
                    "groups_id": [(6, 0, [self.group.id])],
                    "content": self._doc_link(self.attachment.id, count=2),
                }
            )

    def test_rewriting_is_idempotent(self):
        self.assertEqual(
            self.head.content,
            self.head._rewrite_download_links(self.head.content),
        )

    def test_inline_image_is_not_tracked(self):
        page = self.env["document.page"].create(
            {
                "name": "With image",
                "type": "content",
                "groups_id": [(6, 0, [self.group.id])],
                "content": '<p><img src="/web/image/%s" /></p>' % self.attachment.id,
            }
        )
        head = page.history_head
        self.assertFalse(head._tracked_attachment_ids(head.content))
        self.assertNotIn("/document_page_distribution_download_log/", head.content)

    def test_first_download_is_logged(self):
        recipient = self._recipient(self.head, self.alice)
        with freeze_time("2026-06-01 10:00:00"):
            download = self.head.with_user(self.alice)._log_recipient_download(
                self.attachment.id
            )
        self.assertTrue(download)
        self.assertEqual(download.recipient_id, recipient)
        self.assertEqual(download.history_id, self.head)
        self.assertEqual(download.user_id, self.alice)
        self.assertTrue(recipient.downloaded)
        self.assertEqual(recipient.download_count, 1)
        self.assertEqual(recipient.first_download_date, datetime(2026, 6, 1, 10, 0, 0))

    def test_second_download_increments_and_keeps_first(self):
        recipient = self._recipient(self.head, self.alice)
        with freeze_time("2026-06-01 10:00:00"):
            self.head.with_user(self.alice)._log_recipient_download(self.attachment.id)
        with freeze_time("2026-06-05 18:30:00"):
            self.head.with_user(self.alice)._log_recipient_download(self.attachment.id)
        self.assertEqual(recipient.download_count, 2)
        self.assertEqual(recipient.first_download_date, datetime(2026, 6, 1, 10, 0, 0))
        self.assertEqual(recipient.last_download_date, datetime(2026, 6, 5, 18, 30, 0))

    def test_download_without_recipient_is_not_logged(self):
        bob = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Bob",
                    "login": "bob_dpddl",
                    "email": "bob@example.com",
                    "groups_id": [(6, 0, [self.doc_user.id, self.group.id])],
                }
            )
        )
        self.assertFalse(self._recipient(self.head, bob))
        download = self.head.with_user(bob)._log_recipient_download(self.attachment.id)
        self.assertFalse(download)

    def test_attachment_must_belong_to_version(self):
        self.assertTrue(self.head._download_attachment_is_tracked(self.attachment.id))
        self.assertFalse(
            self.head._download_attachment_is_tracked(self.attachment.id + 99999)
        )

    def test_old_version_keeps_its_own_attribution(self):
        v1 = self.head
        recipient_v1 = self._recipient(v1, self.alice)
        self.page.write({"content": "<p>Second version, plain text</p>"})
        v2 = self.page.history_head
        self.assertNotEqual(v1, v2)
        download = v1.with_user(self.alice)._log_recipient_download(self.attachment.id)
        self.assertEqual(download.history_id, v1)
        self.assertEqual(download.recipient_id, recipient_v1)

    def test_revision_relinks_inherited_tracking_link_to_new_version(self):
        v1 = self.head
        route = "/document_page_distribution_download_log/download/%s/%s"
        self.assertIn(route % (v1.id, self.attachment.id), v1.content)
        self.page.write({"content": v1.content + "<p>revised</p>"})
        v2 = self.page.history_head
        self.assertNotEqual(v1, v2)
        self.assertIn(route % (v2.id, self.attachment.id), v2.content)
        self.assertNotIn(route % (v1.id, self.attachment.id), v2.content)
        # A real download of v2 lands on v2's recipient line, not v1's.
        self.page._ensure_distribution_recipients(
            v2, self.page._get_distribution_coverage_users()
        )
        recipient_v2 = self._recipient(v2, self.alice)
        download = v2.with_user(self.alice)._log_recipient_download(self.attachment.id)
        self.assertEqual(download.history_id, v2)
        self.assertEqual(download.recipient_id, recipient_v2)

    def test_user_without_security_group_cannot_read_page(self):
        stranger = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Stranger",
                    "login": "stranger_dpddl",
                    "groups_id": [(6, 0, [self.doc_user.id])],
                }
            )
        )
        with self.assertRaises(AccessError):
            self.page.with_user(stranger).check_access_rule("read")

    def test_download_rows_hidden_from_users_outside_document_groups(self):
        stranger = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Stranger ACL",
                    "login": "stranger_acl_dpddl",
                    "groups_id": [(6, 0, [self.doc_user.id])],
                }
            )
        )
        download = self.head.with_user(self.alice)._log_recipient_download(
            self.attachment.id
        )
        download_model = self.env["document.page.history.recipient.download"]
        self.assertFalse(
            download_model.with_user(stranger).search([("id", "=", download.id)])
        )
        with self.assertRaises(AccessError):
            download.with_user(stranger).read(["id"])
        # users covered by the document's security group keep reading the evidence
        self.assertEqual(
            download_model.with_user(self.alice).search([("id", "=", download.id)]),
            download,
        )

    def test_manager_reads_download_rows_outside_own_groups(self):
        manager = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Manager",
                    "login": "manager_dpddl",
                    "groups_id": [
                        (
                            6,
                            0,
                            [self.env.ref("document_page.group_document_manager").id],
                        )
                    ],
                }
            )
        )
        download = self.head.with_user(self.alice)._log_recipient_download(
            self.attachment.id
        )
        self.assertEqual(
            self.env["document.page.history.recipient.download"]
            .with_user(manager)
            .search([("id", "=", download.id)]),
            download,
        )

    def test_new_page_editor_upload_is_bound_to_the_page(self):
        # the backend editor uploads a NOT-yet-saved page's file with
        # res_model='document.page' but res_id=0 plus an access_token the
        # rewrite strips; saving must adopt the orphan so any reader of the
        # page can be served the file by /web/content
        orphan = self.env["ir.attachment"].create(
            {
                "name": "draft.pdf",
                "datas": base64.b64encode(b"%PDF-1.4 draft").decode(),
                "res_model": "document.page",
                "res_id": 0,
            }
        )
        page = self.env["document.page"].create(
            {
                "name": "Authored from scratch",
                "type": "content",
                "groups_id": [(6, 0, [self.group.id])],
                "content": '<p><a href="/web/content/%s?access_token=x">f</a></p>'
                % orphan.id,
            }
        )
        self.assertEqual(orphan.res_id, page.id)

    def test_foreign_attachment_is_not_adopted(self):
        # an attachment of another model, bound to another record, or
        # uploaded by another user must never be rebound by the rewrite
        partner = self.env["res.partner"].create({"name": "Other owner"})
        foreign = self.env["ir.attachment"].create(
            {
                "name": "foreign.pdf",
                "datas": base64.b64encode(b"%PDF-1.4 foreign").decode(),
                "res_model": "res.partner",
                "res_id": partner.id,
            }
        )
        self.env["document.page"].create(
            {
                "name": "Links a foreign file",
                "type": "content",
                "groups_id": [(6, 0, [self.group.id])],
                "content": '<p><a href="/web/content/%s">f</a></p>' % foreign.id,
            }
        )
        self.assertEqual(foreign.res_model, "res.partner")
        self.assertEqual(foreign.res_id, partner.id)

    def test_web_content_url_variants_resolve_to_attachment(self):
        # the parser must recognise every shape Odoo emits, including the
        # slugged /web/content/<id>-name.pdf that was previously missed
        aid = self.attachment.id
        for href in (
            "/web/content/%s" % aid,
            "/web/content/%s?download=true" % aid,
            "/web/content/%s-procedure.pdf" % aid,
            "/web/content/ir.attachment/%s/datas" % aid,
        ):
            self.assertEqual(
                self.head._download_link_attachment_id(href),
                aid,
                "URL not recognised: %s" % href,
            )

    def test_slugified_pdf_link_is_rewritten(self):
        page = self.env["document.page"].create(
            {
                "name": "Slug link",
                "type": "content",
                "groups_id": [(6, 0, [self.group.id])],
                "content": '<p><a href="/web/content/%s-procedure.pdf">f</a></p>'
                % self.attachment.id,
            }
        )
        head = page.history_head
        route = "/document_page_distribution_download_log/download/%s/%s" % (
            head.id,
            self.attachment.id,
        )
        self.assertIn(route, head.content)

    def test_non_pdf_link_is_not_tracked(self):
        notes = self.env["ir.attachment"].create(
            {
                "name": "notes.txt",
                "datas": base64.b64encode(b"just text").decode(),
            }
        )
        self.assertNotEqual(notes.mimetype, "application/pdf")
        page = self.env["document.page"].create(
            {
                "name": "Non-PDF link",
                "type": "content",
                "groups_id": [(6, 0, [self.group.id])],
                "content": '<p><a href="/web/content/%s">notes</a></p>' % notes.id,
            }
        )
        head = page.history_head
        # left untouched: not rewritten, not tracked
        self.assertIn('/web/content/%s"' % notes.id, head.content)
        self.assertNotIn("/document_page_distribution_download_log/", head.content)
        self.assertFalse(head._tracked_attachment_ids(head.content))

    def test_non_pdf_link_does_not_trip_single_document_rule(self):
        # one PDF + one non-PDF must save fine: only the PDF is a document
        notes = self.env["ir.attachment"].create(
            {
                "name": "annex.txt",
                "datas": base64.b64encode(b"annex text").decode(),
            }
        )
        page = self.env["document.page"].create(
            {
                "name": "PDF plus non-PDF",
                "type": "content",
                "groups_id": [(6, 0, [self.group.id])],
                "content": '<p><a href="/web/content/%s">pdf</a>'
                '<a href="/web/content/%s">txt</a></p>'
                % (self.attachment.id, notes.id),
            }
        )
        head = page.history_head
        route = "/document_page_distribution_download_log/download/%s/%s" % (
            head.id,
            self.attachment.id,
        )
        self.assertIn(route, head.content)  # the PDF is tracked
        self.assertIn('/web/content/%s"' % notes.id, head.content)  # the txt is not

    def test_opening_page_does_not_log_download(self):
        # merely reading the page/version content must not create evidence;
        # a download is only logged by the controller click
        download_model = self.env["document.page.history.recipient.download"]
        before = download_model.search_count([])
        self.page.with_user(self.alice).read(["content"])
        self.head.with_user(self.alice).read(["content"])
        self.assertEqual(download_model.search_count([]), before)
