# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dev1@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import Form, TransactionCase, tagged


# post_install: the companies created here need every module of the database
@tagged("post_install", "-at_install")
class TestMgmtsystemDocumentMasterFolder(TransactionCase):
    def setUp(self):
        super().setUp()
        self.page_model = self.env["document.page"]
        self.company_a = self.env["res.company"].create({"name": "Company A"})
        self.company_b = self.env["res.company"].create({"name": "Company B"})
        self.company_c = self.env["res.company"].create({"name": "Company C"})
        # With document_page_procedure_master_folder installed, the OCA
        # procedures category already holds the mark, with or without company
        self.page_model.with_context(active_test=False).search(
            [("mgmtsystem_master_folder", "=", "procedure")]
        ).mgmtsystem_master_folder = False
        self.shared_folder = self.page_model.create(
            {
                "name": "Procedures without company",
                "type": "category",
                "company_id": False,
                "mgmtsystem_master_folder": "procedure",
                "template": "<p>Procedure template</p>",
            }
        )
        self.folder_a = self.page_model.create(
            {
                "name": "Procedures of A",
                "type": "category",
                "company_id": self.company_a.id,
                "mgmtsystem_master_folder": "procedure",
            }
        )
        self.folder_b = self.page_model.create(
            {
                "name": "Procedures of B",
                "type": "category",
                "company_id": self.company_b.id,
                "mgmtsystem_master_folder": "procedure",
            }
        )
        self.user = self.env["res.users"].create(
            {
                "name": "Procedure reader",
                "login": "procedure_reader",
                "company_id": self.company_a.id,
                "company_ids": [
                    (6, 0, (self.company_a | self.company_b | self.company_c).ids)
                ],
                "groups_id": [
                    (6, 0, [self.env.ref("knowledge.group_document_user").id])
                ],
            }
        )

    def _proposed_folder(self, companies):
        """The category that Create of a procedures menu proposes to the user
        with these companies active; the first one is the selected company."""
        values = (
            self.page_model.with_user(self.user)
            .with_context(
                allowed_company_ids=companies.ids,
                mgmtsystem_master_folder_menu="procedure",
            )
            .default_get(["parent_id"])
        )
        return self.page_model.browse(values["parent_id"])

    def test_create_proposes_folder_of_selected_company(self):
        """Create proposes the master folder of the selected company, also when
        another company with its own master folder is active."""
        self.assertEqual(self._proposed_folder(self.company_a), self.folder_a)
        self.assertEqual(
            self._proposed_folder(self.company_b | self.company_a), self.folder_b
        )

    def test_create_falls_back_to_folder_without_company(self):
        """A company without its own master folder gets the one without
        company."""
        self.assertEqual(self._proposed_folder(self.company_c), self.shared_folder)

    def test_create_files_page_with_template_and_selected_company(self):
        """The page created from the menu goes in the proposed master folder,
        starts from its template and belongs to the selected company."""
        editor = self.env["res.users"].create(
            {
                "name": "Procedure editor",
                "login": "procedure_editor",
                "company_id": self.company_c.id,
                "company_ids": [(6, 0, (self.company_c | self.company_a).ids)],
                "groups_id": [
                    (6, 0, [self.env.ref("document_page.group_document_editor").id])
                ],
            }
        )
        # Company C has no master folder of its own: the page goes in the one
        # without company, not in the one of company A, which is also active,
        # and it still belongs to company C
        page_form = Form(
            self.page_model.with_user(editor).with_context(
                allowed_company_ids=(self.company_c | self.company_a).ids,
                mgmtsystem_master_folder_menu="procedure",
            ),
            view="document_page.view_wiki_form",
        )
        page_form.name = "Procedure of C"
        page_form.draft_name = "Rev 01"
        page_form.draft_summary = "First version"
        page = page_form.save()
        self.assertEqual(page.parent_id, self.shared_folder)
        self.assertEqual(page.content, self.shared_folder.template)
        self.assertEqual(page.company_id, self.company_c)

    def test_create_without_any_master_folder_raises(self):
        """A company without its own master folder, and no master folder
        without company: Create says so."""
        self.shared_folder.mgmtsystem_master_folder = False
        with self.assertRaisesRegex(UserError, "Company C"):
            self._proposed_folder(self.company_c)

    def test_create_with_several_master_folders_raises(self):
        """Two master folders of one menu in one company: Create names them."""
        # The constraint refuses this through the ORM, so it is written in SQL
        duplicate = self.page_model.create(
            {
                "name": "Old procedures of A",
                "type": "category",
                "company_id": self.company_a.id,
            }
        )
        self.env.cr.execute(
            "UPDATE document_page SET mgmtsystem_master_folder = 'procedure' "
            "WHERE id = %s",
            (duplicate.id,),
        )
        self.page_model.invalidate_cache()
        with self.assertRaisesRegex(UserError, "Old procedures of A"):
            self._proposed_folder(self.company_a)

    def test_only_category_can_be_master_folder(self):
        page = self.page_model.create(
            {
                "name": "Procedure of A",
                "parent_id": self.folder_a.id,
                "company_id": self.company_a.id,
                "content": "Test",
            }
        )
        with self.assertRaises(ValidationError), self.cr.savepoint():
            page.mgmtsystem_master_folder = "manual"

    def test_one_master_folder_per_menu_and_company(self):
        """A second master folder of a menu in the same company, or a second one
        without company, is refused; another menu is allowed."""
        with self.assertRaisesRegex(
            ValidationError, "Procedures of A"
        ), self.cr.savepoint():
            self.page_model.create(
                {
                    "name": "More procedures of A",
                    "type": "category",
                    "company_id": self.company_a.id,
                    "mgmtsystem_master_folder": "procedure",
                }
            )
        with self.assertRaisesRegex(
            ValidationError, "Procedures without company"
        ), self.cr.savepoint():
            self.page_model.create(
                {
                    "name": "More procedures without company",
                    "type": "category",
                    "company_id": False,
                    "mgmtsystem_master_folder": "procedure",
                }
            )
        manuals_a = self.page_model.create(
            {
                "name": "Manuals of A",
                "type": "category",
                "company_id": self.company_a.id,
                "mgmtsystem_master_folder": "manual",
            }
        )
        self.assertEqual(manuals_a.mgmtsystem_master_folder, "manual")

    def test_one_master_folder_per_menu_and_company_unseen(self):
        """The mark stays unique when the writer cannot read the category that
        already has it."""
        editor = self.env["res.users"].create(
            {
                "name": "Procedure editor",
                "login": "procedure_editor",
                "company_id": self.company_a.id,
                "company_ids": [(6, 0, self.company_a.ids)],
                "groups_id": [
                    (6, 0, [self.env.ref("document_page.group_document_editor").id])
                ],
            }
        )
        self.env["ir.rule"].create(
            {
                "name": "Hide the procedures of A",
                "model_id": self.env.ref("document_page.model_document_page").id,
                "domain_force": "[('id', '!=', %d)]" % self.folder_a.id,
                "perm_read": True,
                "perm_write": False,
                "perm_create": False,
                "perm_unlink": False,
            }
        )
        with self.assertRaisesRegex(
            ValidationError, "Procedures of A"
        ), self.cr.savepoint():
            self.page_model.with_user(editor).create(
                {
                    "name": "More procedures of A",
                    "type": "category",
                    "company_id": self.company_a.id,
                    "mgmtsystem_master_folder": "procedure",
                }
            )

    def test_master_folder_cannot_be_archived(self):
        """A category cannot be archived while it is the master folder of a menu."""
        values = {"active": False}
        # document_page_archive_reason, when installed in the same database,
        # refuses to archive a page without a reason
        if "archive_reason" in self.folder_a._fields:
            values["archive_reason"] = "Replaced by another folder"
        with self.assertRaisesRegex(
            ValidationError, 'Clear its "Master Folder Of" field'
        ), self.cr.savepoint():
            self.folder_a.write(values)
        self.assertTrue(self.folder_a.active)
