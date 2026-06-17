# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDocumentPageAttachmentSearch(TransactionCase):
    """Covers the ``document.page`` "Content" search extension: matching the
    indexed text of the files attached to the page (resolved by the native
    ``res_model``/``res_id`` link, not by parsing the page HTML), respecting the
    user's access to the page, and the ``reindex_attachment_content`` helper.

    Run as ``post_install`` so the full registry is loaded. The ACL test reads
    ``document.page`` as a non-superuser; on a database that also has
    ``document_page_group`` installed its global rule references that module's
    ``group_ids`` field, which is not registered at ``at_install`` (this module
    loads before ``document_page_group``), so the rule would fail to parse.
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

    def test_attachment_matched_by_res_id_not_body_link(self):
        # New semantics: a file is matched because it is attached to the page
        # (res_model/res_id), regardless of whether it is linked in the body.
        self._attach(self.page_html, "extra.txt", b"this file says EXTRAWORD")
        result = self._search_content("EXTRAWORD")
        self.assertIn(self.page_html, result)

    def test_attachment_without_res_id_is_ignored(self):
        # A file uploaded before the page is saved gets res_id=0 and cannot be
        # mapped back to a page, so it is not matched.
        attachment = self._attach(
            self.page_empty, "noanchor.txt", b"this has NOANCHORWORD content"
        )
        attachment.res_id = 0
        result = self._search_content("NOANCHORWORD")
        self.assertNotIn(self.page_empty, result)

    def test_attachment_of_missing_page_does_not_crash(self):
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
        self._attach(page, "first.txt", b"first file says MULTIWORDA")
        self._attach(page, "second.txt", b"second file says MULTIWORDB")
        self.assertIn(page, self._search_content("MULTIWORDA"))
        self.assertIn(page, self._search_content("MULTIWORDB"))

    def _orphan(self, name, raw):
        return self.Attachment.create(
            {
                "name": name,
                "res_model": "document.page",
                "res_id": 0,
                "datas": base64.b64encode(raw),
                "mimetype": "text/plain",
            }
        )

    def test_anchor_sets_res_id_when_embedded_before_save(self):
        orphan = self._orphan("embedded.txt", b"the file says ANCHORWORD")
        page = self.DocumentPage.create(
            {
                "name": "Page Anchor Create",
                "type": "content",
                "parent_id": self.category.id,
                "content": '<a href="/web/content/%d">file</a>' % orphan.id,
            }
        )
        self.assertEqual(orphan.res_id, page.id)
        self.assertIn(page, self._search_content("ANCHORWORD"))

    def test_anchor_sets_res_id_on_write(self):
        orphan = self._orphan("embedded2.txt", b"the file says ANCHORWRITE")
        page = self.DocumentPage.create(
            {
                "name": "Page Anchor Write",
                "type": "content",
                "parent_id": self.category.id,
            }
        )
        page.write({"content": '<a href="/web/content/%d">file</a>' % orphan.id})
        self.assertEqual(orphan.res_id, page.id)
        self.assertIn(page, self._search_content("ANCHORWRITE"))

    def test_anchor_does_not_steal_attachment_of_another_page(self):
        owned = self._attach(self.page_html, "owned.txt", b"the file says OWNEDWORD")
        self.DocumentPage.create(
            {
                "name": "Page Anchor Steal",
                "type": "content",
                "parent_id": self.category.id,
                "content": '<a href="/web/content/%d">file</a>' % owned.id,
            }
        )
        self.assertEqual(owned.res_id, self.page_html.id)

    def test_reindex_indexes_missing_content(self):
        page = self.DocumentPage.create(
            {
                "name": "Page Reindex",
                "type": "content",
                "parent_id": self.category.id,
            }
        )
        attachment = self._attach(page, "migrated.txt", b"the file says REINDEXWORD")
        attachment.index_content = False
        self.assertNotIn(page, self._search_content("REINDEXWORD"))
        result = page.reindex_attachment_content()
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
        attachment.index_content = False
        result = page.reindex_attachment_content()
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
        self._attach(page, "indexed.txt", b"already indexed SKIPWORDA")
        dataless = self._attach(page, "dataless.txt", b"to be emptied SKIPWORDB")
        dataless.datas = False
        dataless.index_content = False
        result = page.reindex_attachment_content()
        self.assertEqual(result["processed"], 0)
        self.assertEqual(result["skipped"], 2)
        self.assertEqual(result["no_text"], [])

    def test_reindex_force_with_only_missing_false(self):
        self.attachment.index_content = "stale index"
        self.assertNotIn(self.page_attached, self._search_content("UNIQUEATTACH"))
        result = self.page_attached.reindex_attachment_content(only_missing=False)
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
        (first + second).write({"index_content": False})
        result = page.reindex_attachment_content(batch_size=1)
        self.assertEqual((result["processed"], result["skipped"]), (1, 0))
        result = page.reindex_attachment_content(batch_size=1)
        self.assertEqual((result["processed"], result["skipped"]), (1, 1))
        result = page.reindex_attachment_content(batch_size=1)
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
        attachment.index_content = False
        result = self.DocumentPage.reindex_attachment_content()
        # The model-level call covers every document.page attachment, so on a
        # shared database other unindexed attachments may exhaust the batch
        # before this one: assert only the contract of the call.
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
        self._attach(restricted_page, "secret.txt", b"the file says RESTRICTEDWORD")
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
        result = self.DocumentPage.with_user(user).search(
            [("content", "ilike", "RESTRICTEDWORD")]
        )
        self.assertNotIn(restricted_page, result)
