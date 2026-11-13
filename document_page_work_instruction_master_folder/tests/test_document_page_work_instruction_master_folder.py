# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dev1@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged
from odoo.tools.safe_eval import safe_eval


# post_install: the companies created here need every module of the database
@tagged("post_install", "-at_install")
class TestDocumentPageWorkInstructionMasterFolder(TransactionCase):
    def setUp(self):
        super().setUp()
        self.page_model = self.env["document.page"]
        self.action = self.env.ref(
            "document_page_work_instruction.work_instructions_action"
        )
        self.company_a = self.env["res.company"].create({"name": "Company A"})
        self.company_b = self.env["res.company"].create({"name": "Company B"})
        self.folder_a = self.page_model.create(
            {
                "name": "Work instructions of A",
                "type": "category",
                "company_id": self.company_a.id,
                "mgmtsystem_master_folder": "work_instruction",
            }
        )
        self.folder_b = self.page_model.create(
            {
                "name": "Work instructions of B",
                "type": "category",
                "company_id": self.company_b.id,
                "mgmtsystem_master_folder": "work_instruction",
            }
        )
        self.page_a = self.page_model.create(
            {
                "name": "Work instruction of A",
                "parent_id": self.folder_a.id,
                "company_id": self.company_a.id,
                "content": "Test",
            }
        )
        self.page_b = self.page_model.create(
            {
                "name": "Work instruction of B",
                "parent_id": self.folder_b.id,
                "company_id": self.company_b.id,
                "content": "Test",
            }
        )
        self.user = self.env["res.users"].create(
            {
                "name": "Reader",
                "login": "master_folder_reader",
                "company_id": self.company_a.id,
                "company_ids": [(6, 0, (self.company_a | self.company_b).ids)],
                "groups_id": [
                    (6, 0, [self.env.ref("knowledge.group_document_user").id])
                ],
            }
        )

    def test_oca_category_is_master_folder(self):
        """Installing the module makes the OCA category the master folder of the
        menu."""
        category = self.env.ref(
            "document_page_work_instruction.document_page_group_work_instructions"
        )
        self.assertEqual(category.mgmtsystem_master_folder, "work_instruction")

    def test_menu_lists_pages_of_master_folders_of_active_companies(self):
        """The menu lists the pages of the master folders of the active
        companies, and no page of another category."""
        other_category = self.page_model.create(
            {"name": "Drafts of A", "type": "category", "company_id": self.company_a.id}
        )
        page_elsewhere = self.page_model.create(
            {
                "name": "Draft of A",
                "parent_id": other_category.id,
                "company_id": self.company_a.id,
                "content": "Test",
            }
        )
        pages = self.page_model.with_user(self.user)
        both = pages.with_context(
            allowed_company_ids=(self.company_a | self.company_b).ids
        ).search(safe_eval(self.action.domain))
        self.assertIn(self.page_a, both)
        self.assertIn(self.page_b, both)
        self.assertNotIn(page_elsewhere, both)
        only_a = pages.with_context(allowed_company_ids=self.company_a.ids).search(
            safe_eval(self.action.domain)
        )
        self.assertIn(self.page_a, only_a)
        self.assertNotIn(self.page_b, only_a)

    def test_create_proposes_folder_of_selected_company(self):
        """Create in the menu proposes the master folder of the selected
        company."""
        values = (
            self.page_model.with_user(self.user)
            .with_context(
                **safe_eval(self.action.context),
                allowed_company_ids=(self.company_b | self.company_a).ids,
            )
            .default_get(["parent_id"])
        )
        self.assertEqual(values["parent_id"], self.folder_b.id)
