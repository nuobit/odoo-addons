# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestDocumentPageRelatedTour(HttpCase):
    def setUp(self):
        super().setUp()
        self.page_model = self.env["document.page"]
        self.category = self.page_model.create({"name": "Quality", "type": "category"})
        self.env["res.users"].create(
            {
                "name": "editor_test",
                "login": "editor_test",
                "password": "editor_test",
                "email": "editor_test@example.com",
                # the tour looks for English labels
                "lang": "en_US",
                "groups_id": [
                    (6, 0, [self.env.ref("document_page.group_document_editor").id])
                ],
            }
        )

    def _create_page(self, name):
        return self.page_model.create(
            {
                "name": name,
                "type": "content",
                "parent_id": self.category.id,
                "content": "<p>Text</p>",
                "draft_name": "1.0",
                "draft_summary": "First version",
            }
        )

    def test_editor_edits_related_documents_in_the_browser(self):
        procedure = self._create_page("Procedure")
        law = self._create_page("Law")
        self._create_page("Guide")
        action = self.env.ref("document_page.action_page")
        self.start_tour(
            "/web#action=%d&id=%d&model=document.page&view_type=form"
            % (action.id, procedure.id),
            "document_page_related_tour",
            login="editor_test",
            timeout=120,
        )
        procedure.invalidate_cache()
        self.assertEqual(procedure.related_page_ids, law)
