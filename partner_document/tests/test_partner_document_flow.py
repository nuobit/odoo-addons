# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

import base64

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestPartnerDocumentFlow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.passport_type = cls._create_document_type("Passport")
        cls.medical_type = cls._create_document_type("Medical Certificate")
        cls.diver_classification = cls._create_classification(
            "Document Flow Diver",
            cls.passport_type | cls.medical_type,
        )
        cls.non_expiring_type = cls._create_document_type(
            "Permanent License",
            no_expiration=True,
        )
        cls.license_classification = cls._create_classification(
            "Document Flow License Holder",
            cls.non_expiring_type,
        )

    @classmethod
    def _create_document_type(cls, name, no_expiration=False):
        with Form(cls.env["partner.document.type"]) as document_type_form:
            document_type_form.name = name
            document_type_form.no_expiration = no_expiration
        return document_type_form.save()

    @classmethod
    def _create_classification(cls, name, document_types):
        with Form(cls.env["partner.classification"]) as classification_form:
            classification_form.name = name
            for document_type in document_types:
                classification_form.document_type_ids.add(document_type)
        return classification_form.save()

    def _create_partner(self, name, classification):
        with Form(self.env["res.partner"]) as partner_form:
            if "firstname" in self.env["res.partner"]._fields:
                partner_form.firstname = name
                partner_form.lastname = "Test"
            else:
                partner_form.name = name
        partner = partner_form.save()
        with self._open_partner_documents_form(partner) as documents_form:
            documents_form.classification_id = classification
        return documents_form.save()

    def _open_partner_documents_form(self, partner):
        action = partner.action_view_partner_documents()
        view_id = action.get("view_id")
        if isinstance(view_id, (list, tuple)):
            view_id = view_id[0]
        if not view_id:
            view_id = next(
                view[0] for view in action.get("views", []) if view[1] == "form"
            )
        return Form(partner, view=self.env["ir.ui.view"].browse(view_id))

    def _edit_partner_document(self, document, edit):
        partner = self._reload_partner_form(document.partner_id)
        document = partner.document_ids.filtered(lambda doc: doc.id == document.id)
        self.assertEqual(len(document), 1)
        document_index = partner.document_ids.ids.index(document.id)
        with self._open_partner_documents_form(partner) as partner_form:
            with partner_form.document_ids.edit(document_index) as document_form:
                edit(document_form, document)
        partner = partner_form.save()
        return partner.document_ids.filtered(lambda doc: doc.id == document.id)

    def _upload_document(self, document, filename="document.pdf", days=30):
        def edit(document_form, current_document):
            document_form.datas = base64.b64encode(filename.encode())
            if not current_document.no_expiration:
                document_form.expiration_date = fields.Date.add(
                    fields.Date.today(),
                    days=days,
                )

        return self._edit_partner_document(document, edit)

    def _validate_document(self, document):
        def edit(document_form, __):
            document_form.validated = True

        return self._edit_partner_document(document, edit)

    def _reload_partner_form(self, partner):
        self.env.flush_all()
        self.env.invalidate_all()
        with Form(partner):
            pass
        return partner.browse(partner.id)

    def test_partner_form_generates_documents_and_tracks_missing_files(self):
        partner = self._create_partner(
            "Document Flow Missing Files",
            self.diver_classification,
        )

        self.assertEqual(
            set(partner.document_ids.document_type_id.ids),
            set((self.passport_type | self.medical_type).ids),
        )
        self.assertTrue(partner.remain_files)

        for document in partner.document_ids:
            self._upload_document(document)

        partner = self._reload_partner_form(partner)
        self.assertFalse(partner.remain_files)

    def test_user_can_only_validate_a_valid_uploaded_document(self):
        partner = self._create_partner(
            "Document Flow Validation",
            self.diver_classification,
        )
        document = partner.document_ids.filtered(
            lambda doc: doc.document_type_id == self.passport_type
        )

        with self.assertRaises(ValidationError):
            self._validate_document(document)

        self._upload_document(document, days=-1)
        with self.assertRaises(ValidationError):
            self._validate_document(document)

        self._upload_document(document)
        document = self._validate_document(document)
        self.assertTrue(document.validated)
        self.assertEqual(document.validated_by_id, self.env.user)

        def extend_expiration(document_form, __):
            document_form.expiration_date = fields.Date.add(
                fields.Date.today(),
                days=60,
            )

        document = self._edit_partner_document(document, extend_expiration)
        self.assertFalse(document.validated)
        self.assertFalse(document.validated_by_id)

        document = self._validate_document(document)
        self.assertTrue(document.validated)
        self.assertEqual(document.validated_by_id, self.env.user)

        self._upload_document(document, filename="new-passport.pdf")
        self.assertFalse(document.validated)
        self.assertFalse(document.validated_by_id)

    def test_user_can_change_classification_without_losing_uploaded_documents(self):
        partner = self._create_partner(
            "Document Flow Classification Change",
            self.diver_classification,
        )
        passport = partner.document_ids.filtered(
            lambda doc: doc.document_type_id == self.passport_type
        )
        self._upload_document(passport)

        with self._open_partner_documents_form(partner) as partner_form:
            partner_form.classification_id = self.license_classification
        partner = partner_form.save()

        self.assertIn(passport.id, partner.document_ids.ids)
        self.assertIn(
            self.non_expiring_type.id,
            partner.document_ids.document_type_id.ids,
        )
        self.assertIn(
            self.medical_type.id,
            partner.document_ids.document_type_id.ids,
        )
        self.assertTrue(partner.remain_files)

        license_doc = partner.document_ids.filtered(
            lambda doc: doc.document_type_id == self.non_expiring_type
        )
        self._upload_document(license_doc, filename="license.pdf")
        partner = self._reload_partner_form(partner)
        self.assertFalse(partner.remain_files)

    def test_user_can_change_classification_and_drop_empty_documents(self):
        partner = self._create_partner(
            "Document Flow Empty Classification Change",
            self.diver_classification,
        )

        with self._open_partner_documents_form(partner) as partner_form:
            partner_form.classification_id = self.license_classification
        partner = partner_form.save()

        self.assertNotIn(
            self.passport_type.id,
            partner.document_ids.document_type_id.ids,
        )
        self.assertNotIn(
            self.medical_type.id,
            partner.document_ids.document_type_id.ids,
        )
        self.assertIn(
            self.non_expiring_type.id,
            partner.document_ids.document_type_id.ids,
        )
