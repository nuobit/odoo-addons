# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDocumentPageAttachmentSearch(TransactionCase):
    """Covers the ``document.page`` "Content" search extension: matching the
    indexed text of files embedded in the page HTML, ignoring attachments no
    longer referenced, respecting the user's access to the page, and the
    ``reindex_linked_attachment_content`` helper.

    Run as ``post_install`` so the full registry is loaded. The ACL test reads
    ``document.page`` as a non-superuser; on a database that also has
    ``document_page_group`` installed its global rule references that module's
    ``group_ids`` field, which is not yet registered at ``at_install`` (this
    module loads before ``document_page_group``), so the rule fails to parse.
    """

    def setUp(self):
        super().setUp()
        self.DocumentPage = self.env["document.page"]
        self.Attachment = self.env["ir.attachment"]
        self.category = self.DocumentPage.create(
            {"name": "Test Category", "type": "category"}
        )
        self.page_html = self.DocumentPage.create(
            {
                "name": "Page With HTML",
                "type": "content",
                "parent_id": self.category.id,
                "content": "<p>visible html keyword UNIQUEHTML</p>",
            }
        )
        self.page_attached = self.DocumentPage.create(
            {
                "name": "Page With Attachment",
                "type": "content",
                "parent_id": self.category.id,
                "content": "<p>nothing relevant here</p>",
            }
        )
        self.page_empty = self.DocumentPage.create(
            {
                "name": "Page Empty",
                "type": "content",
                "parent_id": self.category.id,
                "content": "<p>nothing relevant here</p>",
            }
        )
        self.attachment = self._attach(
            self.page_attached, "evidence.txt", b"talks about UNIQUEATTACH content"
        )
        self.page_attached.content = (
            "<p>nothing relevant here</p>"
            '<a href="/web/content/%d?download=true">file</a>' % self.attachment.id
        )

    def _attach(self, page, name, raw):
        return self.Attachment.create(
            {
                "name": name,
                "res_model": "document.page",
                "res_id": page.id,
                "datas": base64.b64encode(raw),
                "mimetype": "text/plain",
            }
        )

    def _search_content(self, value, operator="ilike"):
        return self.DocumentPage.search([("content", operator, value)])

    def test_html_search_still_works(self):
        result = self._search_content("UNIQUEHTML")
        self.assertIn(self.page_html, result)
        self.assertNotIn(self.page_attached, result)
        self.assertNotIn(self.page_empty, result)

    def test_attachment_indexed_content_is_matched(self):
        self.assertTrue(self.attachment.index_content)
        self.assertIn("UNIQUEATTACH", self.attachment.index_content)
        result = self._search_content("UNIQUEATTACH")
        self.assertIn(self.page_attached, result)
        self.assertNotIn(self.page_html, result)
        self.assertNotIn(self.page_empty, result)

    def test_no_match_returns_empty(self):
        result = self._search_content("NOTHINGMATCHESTHIS")
        self.assertNotIn(self.page_html, result)
        self.assertNotIn(self.page_attached, result)
        self.assertNotIn(self.page_empty, result)

    def test_non_text_operator_falls_back_to_base(self):
        result = self.DocumentPage.search([("content", "=", "UNIQUEATTACH")])
        self.assertNotIn(self.page_attached, result)

    def test_stale_attachment_not_referenced_is_ignored(self):
        self._attach(self.page_html, "stale.txt", b"this is STALEWORD content")
        result = self._search_content("STALEWORD")
        self.assertNotIn(self.page_html, result)

    def test_attachment_linked_without_query_is_matched(self):
        page = self.DocumentPage.create(
            {
                "name": "Page Link No Query",
                "type": "content",
                "parent_id": self.category.id,
            }
        )
        attachment = self._attach(page, "noquery.txt", b"talks about NOQUERYWORD")
        page.content = '<a href="/web/content/%d">file</a>' % attachment.id
        result = self._search_content("NOQUERYWORD")
        self.assertIn(page, result)

    def test_attachment_linked_via_web_image_is_matched(self):
        page = self.DocumentPage.create(
            {
                "name": "Page Link Image",
                "type": "content",
                "parent_id": self.category.id,
            }
        )
        attachment = self._attach(page, "image.txt", b"talks about IMAGEWORD")
        page.content = '<img src="/web/image/%d">' % attachment.id
        result = self._search_content("IMAGEWORD")
        self.assertIn(page, result)

    def test_orphan_attachment_of_missing_page_does_not_crash(self):
        attachment = self._attach(
            self.page_empty, "orphan.txt", b"this has ORPHANWORD content"
        )
        attachment.res_id = self.page_empty.id + 100000
        result = self._search_content("ORPHANWORD")
        self.assertNotIn(self.page_empty, result)

    def test_multiple_attachments_on_page_are_all_searchable(self):
        page = self.DocumentPage.create(
            {
                "name": "Page Multi Attach",
                "type": "content",
                "parent_id": self.category.id,
            }
        )
        first = self._attach(page, "first.txt", b"first file says MULTIWORDA")
        second = self._attach(page, "second.txt", b"second file says MULTIWORDB")
        page.content = (
            '<a href="/web/content/%d">a</a>'
            '<a href="/web/content/%d">b</a>' % (first.id, second.id)
        )
        self.assertIn(page, self._search_content("MULTIWORDA"))
        self.assertIn(page, self._search_content("MULTIWORDB"))

    def test_reindex_linked_attachment_content(self):
        page = self.DocumentPage.create(
            {
                "name": "Page Reindex",
                "type": "content",
                "parent_id": self.category.id,
            }
        )
        attachment = self._attach(page, "migrated.txt", b"the file says REINDEXWORD")
        page.content = '<a href="/web/content/%d">file</a>' % attachment.id
        attachment.index_content = False
        self.assertNotIn(page, self._search_content("REINDEXWORD"))
        result = page.reindex_linked_attachment_content()
        self.assertEqual(result["processed"], 1)
        self.assertIn(page, self._search_content("REINDEXWORD"))

    def test_reindex_reports_attachments_without_extractable_text(self):
        page = self.DocumentPage.create(
            {
                "name": "Page No Text",
                "type": "content",
                "parent_id": self.category.id,
            }
        )
        attachment = self.Attachment.create(
            {
                "name": "scanned.pdf",
                "res_model": "document.page",
                "res_id": page.id,
                "datas": base64.b64encode(b"not a real pdf, no extractable text"),
                "mimetype": "application/pdf",
            }
        )
        page.content = '<a href="/web/content/%d">file</a>' % attachment.id
        attachment.index_content = False
        result = page.reindex_linked_attachment_content()
        self.assertEqual(result["processed"], 1)
        self.assertIn(attachment.id, [aid for aid, _name in result["no_text"]])

    def test_reindex_skips_indexed_and_dataless_attachments(self):
        page = self.DocumentPage.create(
            {
                "name": "Page Skip",
                "type": "content",
                "parent_id": self.category.id,
            }
        )
        indexed = self._attach(page, "indexed.txt", b"already indexed SKIPWORDA")
        dataless = self._attach(page, "dataless.txt", b"to be emptied SKIPWORDB")
        page.content = (
            '<a href="/web/content/%d">a</a>'
            '<a href="/web/content/%d">b</a>' % (indexed.id, dataless.id)
        )
        dataless.datas = False
        dataless.index_content = False
        result = page.reindex_linked_attachment_content()
        self.assertEqual(result["processed"], 0)
        self.assertEqual(result["skipped"], 2)
        self.assertEqual(result["no_text"], [])

    def test_reindex_force_with_only_missing_false(self):
        self.attachment.index_content = "stale index"
        self.assertNotIn(self.page_attached, self._search_content("UNIQUEATTACH"))
        result = self.page_attached.reindex_linked_attachment_content(
            only_missing=False
        )
        self.assertEqual(result["processed"], 1)
        self.assertIn("UNIQUEATTACH", self.attachment.index_content)
        self.assertIn(self.page_attached, self._search_content("UNIQUEATTACH"))

    def test_reindex_batch_size_caps_and_resumes(self):
        page = self.DocumentPage.create(
            {
                "name": "Page Batch",
                "type": "content",
                "parent_id": self.category.id,
            }
        )
        first = self._attach(page, "first.txt", b"first says BATCHWORDA")
        second = self._attach(page, "second.txt", b"second says BATCHWORDB")
        page.content = (
            '<a href="/web/content/%d">a</a>'
            '<a href="/web/content/%d">b</a>' % (first.id, second.id)
        )
        (first + second).write({"index_content": False})
        result = page.reindex_linked_attachment_content(batch_size=1)
        self.assertEqual((result["processed"], result["skipped"]), (1, 0))
        result = page.reindex_linked_attachment_content(batch_size=1)
        self.assertEqual((result["processed"], result["skipped"]), (1, 1))
        result = page.reindex_linked_attachment_content(batch_size=1)
        self.assertEqual((result["processed"], result["skipped"]), (0, 2))
        self.assertIn(page, self._search_content("BATCHWORDA"))
        self.assertIn(page, self._search_content("BATCHWORDB"))

    def test_reindex_called_on_the_model(self):
        page = self.DocumentPage.create(
            {
                "name": "Page Model Reindex",
                "type": "content",
                "parent_id": self.category.id,
            }
        )
        attachment = self._attach(page, "model.txt", b"the file says MODELWORD")
        page.content = '<a href="/web/content/%d">file</a>' % attachment.id
        attachment.index_content = False
        result = self.DocumentPage.reindex_linked_attachment_content()
        # The model-level call covers every content page, so on a shared
        # database other unindexed attachments may exhaust the batch before
        # this one is reached: assert only the contract of the call.
        self.assertEqual(set(result), {"processed", "skipped", "no_text"})
        self.assertGreaterEqual(result["processed"], 1)

    def test_restricted_page_not_searchable_by_unauthorized_user(self):
        restricted_page = self.DocumentPage.create(
            {
                "name": "Restricted Page",
                "type": "content",
                "parent_id": self.category.id,
            }
        )
        attachment = self._attach(
            restricted_page, "secret.txt", b"the file says RESTRICTEDWORD"
        )
        restricted_page.content = '<a href="/web/content/%d">s</a>' % attachment.id
        self.env["ir.rule"].create(
            {
                "name": "Hide restricted page (test)",
                "model_id": self.env["ir.model"]._get("document.page").id,
                "domain_force": "[('id', '!=', %d)]" % restricted_page.id,
                "groups": [(5, 0, 0)],
            }
        )
        user = self.env["res.users"].create(
            {
                "name": "Doc User",
                "login": "docuser_acl_test",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("base.group_user").id,
                            self.env.ref("knowledge.group_document_user").id,
                        ],
                    )
                ],
            }
        )
        self.assertNotIn(restricted_page, self.DocumentPage.with_user(user).search([]))
        visible_attachments = (
            self.env["ir.attachment"]
            .with_user(user)
            .search(
                [
                    ("res_model", "=", "document.page"),
                    ("index_content", "ilike", "RESTRICTEDWORD"),
                ]
            )
        )
        self.assertNotIn(attachment, visible_attachments)
        result = self.DocumentPage.with_user(user).search(
            [("content", "ilike", "RESTRICTEDWORD")]
        )
        self.assertNotIn(restricted_page, result)
