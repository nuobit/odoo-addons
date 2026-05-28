# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.tests.common import TransactionCase


class TestDocumentPageAttachmentSearch(TransactionCase):
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
        # reference the attachment in the page HTML, as the editor would
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
        # equality should not trigger the attachment widening
        result = self.DocumentPage.search([("content", "=", "UNIQUEATTACH")])
        self.assertNotIn(self.page_attached, result)

    def test_stale_attachment_not_referenced_is_ignored(self):
        # attachment linked by res_id but NOT referenced in the page HTML
        # (e.g. replaced/removed in the editor) must not produce a match
        self._attach(self.page_html, "stale.txt", b"this is STALEWORD content")
        result = self._search_content("STALEWORD")
        self.assertNotIn(self.page_html, result)

    def test_attachment_linked_without_query_is_matched(self):
        # the editor may embed the file without the "?download=true" query
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
        # images are embedded as /web/image/<id> rather than /web/content/<id>
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
        # an attachment whose res_id points to a non-existent page (e.g. the
        # page was deleted, leaving the attachment behind) must be skipped,
        # not raise MissingError when reading the page content
        attachment = self._attach(
            self.page_empty, "orphan.txt", b"this has ORPHANWORD content"
        )
        attachment.res_id = self.page_empty.id + 100000
        result = self._search_content("ORPHANWORD")
        self.assertNotIn(self.page_empty, result)

    def test_multiple_attachments_on_page_are_all_searchable(self):
        # a page linking several files is found by content of any of them
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
