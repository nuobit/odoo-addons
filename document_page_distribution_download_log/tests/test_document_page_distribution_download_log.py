# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from datetime import datetime

from freezegun import freeze_time
from psycopg2 import IntegrityError

from odoo.exceptions import AccessError
from odoo.tests.common import SavepointCase
from odoo.tools import mute_logger


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

    def _new_reader(self, name):
        # a reader of the document who joins its group after the distribution
        return (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": name,
                    "login": "%s_dpddl" % name.lower(),
                    "email": "%s@example.com" % name.lower(),
                    "groups_id": [(6, 0, [self.doc_user.id, self.group.id])],
                }
            )
        )

    def _distribute(self, history):
        # the rows a distribution writes: one recipient per user in scope
        self.page._ensure_distribution_recipients(
            history, self.page._get_distribution_coverage_users()
        )

    def test_link_is_rewritten_with_history_id(self):
        route = "/document_page_distribution_download_log/download/%s/%s" % (
            self.head.id,
            self.attachment.id,
        )
        self.assertIn(route, self.head.content)
        self.assertNotIn('"/web/content/%s"' % self.attachment.id, self.head.content)

    def test_file_linked_twice_is_rewritten_twice(self):
        page = self.env["document.page"].create(
            {
                "name": "Same file twice",
                "type": "content",
                "groups_id": [(6, 0, [self.group.id])],
                "content": self._doc_link(self.attachment.id, count=2),
            }
        )
        head = page.history_head
        route = "/document_page_distribution_download_log/download/%s/%s" % (
            head.id,
            self.attachment.id,
        )
        self.assertEqual(head.content.count(route), 2)
        self.assertNotIn("/web/content/", head.content)

    def test_every_file_of_a_version_is_tracked(self):
        notes = self.env["ir.attachment"].create(
            {
                "name": "notes.txt",
                "datas": base64.b64encode(b"just text").decode(),
            }
        )
        page = self.env["document.page"].create(
            {
                "name": "Procedure and annex",
                "type": "content",
                "groups_id": [(6, 0, [self.group.id])],
                "content": '<p><a href="/web/content/%s">pdf</a>'
                '<a href="/web/content/%s">txt</a></p>'
                % (self.attachment.id, notes.id),
            }
        )
        head = page.history_head
        route = "/document_page_distribution_download_log/download/%s/%s"
        self.assertIn(route % (head.id, self.attachment.id), head.content)
        self.assertIn(route % (head.id, notes.id), head.content)
        self.assertNotIn("/web/content/", head.content)
        self.assertEqual(
            head._tracked_attachment_ids(head.content),
            {self.attachment.id, notes.id},
        )

    def test_link_keeps_its_access_token(self):
        page = self.env["document.page"].create(
            {
                "name": "Link with token",
                "type": "content",
                "groups_id": [(6, 0, [self.group.id])],
                "content": '<p><a href="/web/content/%s?access_token=abc'
                '&amp;unique=123&amp;download=true">f</a></p>' % self.attachment.id,
            }
        )
        head = page.history_head
        self.assertIn(
            '"/document_page_distribution_download_log/download/%s/%s'
            '?access_token=abc"' % (head.id, self.attachment.id),
            head.content,
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

    def test_download_of_a_user_who_is_not_a_recipient_is_logged(self):
        bob = self._new_reader("Bob")
        self.assertFalse(self._recipient(self.head, bob))
        download = self.head.with_user(bob)._log_recipient_download(self.attachment.id)
        self.assertEqual(len(download), 1)
        self.assertEqual(download.history_id, self.head)
        self.assertEqual(download.user_id, bob)
        self.assertEqual(download.attachment_id, self.attachment)
        self.assertFalse(download.recipient_id)

    def test_download_made_before_the_distribution_counts_after_it(self):
        bob = self._new_reader("Bob")
        download = self.head.with_user(bob)._log_recipient_download(self.attachment.id)
        self._distribute(self.head)
        recipient = self._recipient(self.head, bob)
        self.assertEqual(len(recipient), 1)
        self.assertEqual(download.recipient_id, recipient)
        self.assertTrue(recipient.downloaded)
        self.assertEqual(recipient.download_count, 1)
        self.assertEqual(self.head.download_summary, "1/2")

    def test_download_outlives_its_recipient(self):
        recipient = self._recipient(self.head, self.alice)
        download = self.head.with_user(self.alice)._log_recipient_download(
            self.attachment.id
        )
        self.assertEqual(download.recipient_id, recipient)
        recipient.unlink()
        self.assertTrue(download.exists())
        self.assertFalse(download.recipient_id)
        self.assertEqual(download.history_id, self.head)
        self.assertEqual(download.user_id, self.alice)

    def test_summary_counts_the_recipients_who_downloaded(self):
        self._new_reader("Bob")
        self._distribute(self.head)
        self.head.with_user(self.alice)._log_recipient_download(self.attachment.id)
        self.head.with_user(self.alice)._log_recipient_download(self.attachment.id)
        self.assertEqual(self.head.distribution_count, 2)
        self.assertEqual(self.head.download_recipient_count, 1)
        self.assertEqual(self.head.download_summary, "1/2")

    def test_summary_does_not_count_a_user_who_is_not_a_recipient(self):
        bob = self._new_reader("Bob")
        self.head.with_user(bob)._log_recipient_download(self.attachment.id)
        self.assertEqual(self.head.distribution_count, 1)
        self.assertEqual(self.head.download_recipient_count, 0)
        self.assertEqual(self.head.download_summary, "0/1")

    def test_version_without_recipients_has_no_download_summary(self):
        page = self.env["document.page"].create(
            {
                "name": "Never distributed",
                "type": "content",
                "groups_id": [(6, 0, [self.group.id])],
                "content": self._doc_link(self.attachment.id),
            }
        )
        head = page.history_head
        head.with_user(self.alice)._log_recipient_download(self.attachment.id)
        self.assertEqual(head.distribution_count, 0)
        self.assertEqual(head.download_recipient_count, 0)
        self.assertFalse(head.download_summary)

    def test_version_with_downloads_cannot_be_deleted(self):
        # a version without recipients, so that only the download holds it
        page = self.env["document.page"].create(
            {
                "name": "Never distributed",
                "type": "content",
                "groups_id": [(6, 0, [self.group.id])],
                "content": self._doc_link(self.attachment.id),
            }
        )
        head = page.history_head
        head.with_user(self.alice)._log_recipient_download(self.attachment.id)
        with self.assertRaises(IntegrityError) as error, mute_logger("odoo.sql_db"):
            with self.cr.savepoint():
                head.unlink()
        self.assertEqual(
            error.exception.diag.constraint_name,
            "document_page_history_recipient_download_history_id_fkey",
        )
        self.assertTrue(head.exists())

    def test_document_with_downloads_cannot_be_deleted(self):
        page = self.env["document.page"].create(
            {
                "name": "Never distributed",
                "type": "content",
                "groups_id": [(6, 0, [self.group.id])],
                "content": self._doc_link(self.attachment.id),
            }
        )
        page.history_head.with_user(self.alice)._log_recipient_download(
            self.attachment.id
        )
        with self.assertRaises(IntegrityError) as error, mute_logger("odoo.sql_db"):
            with self.cr.savepoint():
                page.unlink()
        self.assertEqual(
            error.exception.diag.constraint_name,
            "document_page_history_recipient_download_history_id_fkey",
        )
        self.assertTrue(page.exists())

    def test_file_with_downloads_cannot_be_deleted(self):
        self.head.with_user(self.alice)._log_recipient_download(self.attachment.id)
        with self.assertRaises(IntegrityError) as error, mute_logger("odoo.sql_db"):
            with self.cr.savepoint():
                self.attachment.unlink()
        self.assertEqual(
            error.exception.diag.constraint_name,
            "document_page_history_recipient_download_attachment_id_fkey",
        )
        self.assertTrue(self.attachment.exists())

    def test_file_without_downloads_can_be_deleted(self):
        self.attachment.unlink()
        self.assertFalse(self.attachment.exists())

    def test_download_without_file_is_refused(self):
        with self.assertRaises(IntegrityError) as error, mute_logger("odoo.sql_db"):
            with self.cr.savepoint():
                self.env["document.page.history.recipient.download"].create(
                    {"history_id": self.head.id, "user_id": self.alice.id}
                )
        self.assertEqual(error.exception.diag.column_name, "attachment_id")

    def test_no_user_can_change_the_download_log(self):
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
        download = (
            self.head.with_user(self.alice)
            ._log_recipient_download(self.attachment.id)
            .with_user(manager)
        )
        with self.assertRaises(AccessError):
            download.write({"attachment_id": False})
        with self.assertRaises(AccessError):
            download.unlink()
        with self.assertRaises(AccessError):
            download.create(
                {
                    "history_id": self.head.id,
                    "user_id": manager.id,
                    "attachment_id": self.attachment.id,
                }
            )

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

    def test_opening_page_does_not_log_download(self):
        # merely reading the page/version content must not create evidence;
        # a download is only logged by the controller click
        download_model = self.env["document.page.history.recipient.download"]
        before = download_model.search_count([])
        self.page.with_user(self.alice).read(["content"])
        self.head.with_user(self.alice).read(["content"])
        self.assertEqual(download_model.search_count([]), before)
