# Copyright 2021 Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _
from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)


class TestProductUniqueInternalReference(SavepointCase):
    def test_01_template_vs_template_ok_same_company(self):
        """
        PRE:    - template1 exists
                - template1 has default_code 'sku1'
                - template1 has company1
        ACT:    - create template2
                - template2 has default_code 'sku2'
        POST:   - template2 is created correctly
        """
        # ARRANGE
        company1 = self.env["res.company"].create(
            {
                "name": "Company 1",
            }
        )
        self.env["product.template"].create(
            {
                "name": "Product 1",
                "default_code": "sku1",
                "company_id": company1.id,
            }
        )
        # ACT & ASSERT
        try:
            self.env["product.template"].create(
                {
                    "name": "Product 2",
                    "default_code": "sku2",
                    "company_id": company1.id,
                }
            )
        except ValidationError:
            self.fail(
                _(
                    "The Internal References are not equal, "
                    "this should have not raised an Exception"
                )
            )

    def test_02_template_vs_template_ok_diff_company(self):
        """
        PRE:    - template1 exists
                - template1 has default_code 'sku1'
                - template1 has company1
        ACT:    - create template2
                - template2 has company2
                - template2 has default_code 'sku2'
        POST:   - template2 is created correctly
        """
        # ARRANGE
        company1 = self.env["res.company"].create(
            {
                "name": "Company 1",
            }
        )
        self.env["product.template"].create(
            {
                "name": "Product 1",
                "default_code": "sku1",
                "company_id": company1.id,
            }
        )
        company2 = self.env["res.company"].create(
            {
                "name": "Company 2",
            }
        )
        # ACT & ASSERT
        try:
            self.env["product.template"].create(
                {
                    "name": "Product 2",
                    "default_code": "sku2",
                    "company_id": company2.id,
                }
            )
        except ValidationError:
            self.fail(
                _(
                    "The Internal References are not equal, "
                    "this should have not raised an Exception"
                )
            )

    def test_03_template_vs_template_dup_same_company(self):
        """
        PRE:    - template1 exists
                - template1 has default_code 'sku1'
                - template1 has company1
        ACT:    - create template2
                - template2 has default_code 'sku1'
                - template2 has company1
        POST:   - template2 is not created because exists
                  template1 with same default_code 'sku1'
                  on the same company1
        """
        # ARRANGE
        company1 = self.env["res.company"].create(
            {
                "name": "Company 1",
            }
        )
        self.env["product.template"].create(
            {
                "name": "Product 1",
                "default_code": "sku1",
                "company_id": company1.id,
            }
        )
        # ACT & ASSERT
        try:
            with self.assertRaises(ValidationError):
                self.env["product.template"].create(
                    {
                        "name": "Product 2",
                        "default_code": "sku1",
                        "company_id": company1.id,
                    }
                )
        except AssertionError:
            self.fail(
                _(
                    "It has been possible to create two product templates "
                    "with the same Internal Reference"
                )
            )

    def test_04_template_vs_template_dup_diff_company(self):
        """
        PRE:    - template1 exists
                - template1 has default_code 'sku1'
                - template1 has company1
        ACT:    - create template2
                - template2 has default_code 'sku1'
                - template2 has company2
        POST:   - template2 is created correctly
        """
        # ARRANGE
        company1 = self.env["res.company"].create(
            {
                "name": "Company 1",
            }
        )
        self.env["product.template"].create(
            {
                "name": "Product 1",
                "default_code": "sku1",
                "company_id": company1.id,
            }
        )
        company2 = self.env["res.company"].create(
            {
                "name": "Company 2",
            }
        )
        # ACT & ASSERT
        try:
            self.env["product.template"].create(
                {
                    "name": "Product 2",
                    "default_code": "sku1",
                    "company_id": company2.id,
                }
            )
        except ValidationError:
            self.fail(
                _(
                    "The Internal References are not equal, "
                    "this should have not raised an Exception"
                )
            )

    def test_05_template_vs_template_dup_company_vs_nocompany(self):
        """
        PRE:    - template1 exists
                - template1 has default_code 'sku1'
                - template1 has company1
        ACT:    - create template2
                - template2 has default_code 'sku1'
                - template2 has no company
        POST:   - template2 is not created because exists
                  template1 with same default_code 'sku1'
                  on company1 and template2 has no company
                  which means 'all companies'
        """
        # ARRANGE
        company1 = self.env["res.company"].create(
            {
                "name": "Company 1",
            }
        )
        self.env["product.template"].create(
            {
                "name": "Product 1",
                "default_code": "sku1",
                "company_id": company1.id,
            }
        )
        # ACT & ASSERT
        try:
            with self.assertRaises(ValidationError):
                self.env["product.template"].create(
                    {
                        "name": "Product 2",
                        "default_code": "sku1",
                        "company_id": False,
                    }
                )
        except AssertionError:
            self.fail(
                _(
                    "It has been possible to create a product template on "
                    "one company and another without company with the same "
                    "Internal Reference"
                )
            )

    def test_06_product_vs_template_uniq_same_company(self):
        """
        PRE:    - template1 exists
                - template1 has variant11 and variant12
                - variant11 has default_code 'sku1'
                - variant12 has default_code 'sku2'
                - template1 has company1
        ACT:    - create template2
                - template2 has default_code 'sku2'
                - template2 has company1
        POST:   - template2 is not created because exists
                  variant12 with same default_code 'sku1'
                  on the same company1
        """
        # ARRANGE
        company1 = self.env["res.company"].create(
            {
                "name": "Company 1",
            }
        )
        attribute = self.env["product.attribute"].create(
            {
                "name": "Attribute 1",
                "create_variant": "always",
                "value_ids": [
                    (0, 0, {"name": "Attribute Value 1"}),
                    (0, 0, {"name": "Attribute Value 2"}),
                ],
            }
        )
        template = self.env["product.template"].create(
            {
                "name": "Product 1",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, attribute.value_ids.ids)],
                        },
                    )
                ],
                "company_id": company1.id,
            }
        )
        template.product_variant_ids[0].default_code = "sku1"
        template.product_variant_ids[1].default_code = "sku2"
        # ACT & ASSERT
        try:
            with self.assertRaises(ValidationError):
                self.env["product.template"].create(
                    {
                        "name": "Product 2",
                        "default_code": "sku2",
                        "company_id": company1.id,
                    }
                )
        except AssertionError:
            self.fail(
                _(
                    "It has been possible to create a product template "
                    "when a variant of another template has the same "
                    "Internal Reference"
                )
            )

    def test_07_product_vs_product_uniq_same_company(self):
        """
        PRE:    - template1 exists
                - template1 has variant11 and variant12
                - variant11 has default_code 'sku1'
                - variant12 has default_code 'sku2'
                - template1 has company1
        ACT:    - create template2
                - template2 has company1
                - template2 has variant21 and variant22 and variant23
                - variant21 has default_code 'sku4'
                - variant22 has default_code 'sku3'
                - variant23 has default_code 'sku2'
        POST:   - template2 is not created because exists
                  variant23 with same default_code 'sku1'
                  as variant12 on the same company1
        """
        # ARRANGE
        company1 = self.env["res.company"].create(
            {
                "name": "Company 1",
            }
        )
        attribute1 = self.env["product.attribute"].create(
            {
                "name": "Attribute 1",
                "create_variant": "always",
                "value_ids": [
                    (0, 0, {"name": "Attribute Value 1"}),
                    (0, 0, {"name": "Attribute Value 2"}),
                ],
            }
        )
        template1 = self.env["product.template"].create(
            {
                "name": "Product 1",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute1.id,
                            "value_ids": [(6, 0, attribute1.value_ids.ids)],
                        },
                    )
                ],
                "company_id": company1.id,
            }
        )
        template1.product_variant_ids[0].default_code = "sku1"
        template1.product_variant_ids[1].default_code = "sku2"

        attribute2 = self.env["product.attribute"].create(
            {
                "name": "Attribute 2",
                "create_variant": "always",
                "value_ids": [
                    (0, 0, {"name": "Attribute Value 3"}),
                    (0, 0, {"name": "Attribute Value 4"}),
                    (0, 0, {"name": "Attribute Value 5"}),
                ],
            }
        )
        template2 = self.env["product.template"].create(
            {
                "name": "Product 2",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute2.id,
                            "value_ids": [(6, 0, attribute2.value_ids.ids)],
                        },
                    )
                ],
                "company_id": company1.id,
            }
        )

        # ACT & ASSERT
        try:
            with self.assertRaises(ValidationError):
                template2.product_variant_ids[0].default_code = "sku4"
                template2.product_variant_ids[1].default_code = "sku3"
                template2.product_variant_ids[2].default_code = "sku2"
        except AssertionError:
            self.fail(
                _(
                    "It has been possible to create a product variant "
                    "when a variant of another template has the same "
                    "Internal Reference"
                )
            )

    def test_08_product_vs_product_dup_company_vs_nocompany(self):
        """
        PRE:    - template1 exists
                - template1 has variant11 and variant12
                - variant11 has default_code 'sku1'
                - variant12 has default_code 'sku2'
                - template1 has company1
                - template2 exists
                - template2 has no company
                - template2 has variant21 and variant22 and variant23
                - variant21, variant22, variant23 has no default_code
        ACT:    - change variant21 default_code to 'sku4'
                - change variant22 default_code to 'sku3'
                - change variant23 default_code to 'sku2'
        POST:   - variant default_code are not updated because
                  variant23 has the same default_code as variant12 'sku2'
                  and they belong to the same company1 because
                  template2 has no company and it means 'all companies'
        """
        # ARRANGE
        company1 = self.env["res.company"].create(
            {
                "name": "Company 1",
            }
        )
        attribute1 = self.env["product.attribute"].create(
            {
                "name": "Attribute 1",
                "create_variant": "always",
                "value_ids": [
                    (0, 0, {"name": "Attribute Value 1"}),
                    (0, 0, {"name": "Attribute Value 2"}),
                ],
            }
        )
        template1 = self.env["product.template"].create(
            {
                "name": "Product 1",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute1.id,
                            "value_ids": [(6, 0, attribute1.value_ids.ids)],
                        },
                    )
                ],
                "company_id": company1.id,
            }
        )
        template1.product_variant_ids[0].default_code = "sku1"
        template1.product_variant_ids[1].default_code = "sku2"

        attribute2 = self.env["product.attribute"].create(
            {
                "name": "Attribute 2",
                "create_variant": "always",
                "value_ids": [
                    (0, 0, {"name": "Attribute Value 3"}),
                    (0, 0, {"name": "Attribute Value 4"}),
                    (0, 0, {"name": "Attribute Value 5"}),
                ],
            }
        )
        template2 = self.env["product.template"].create(
            {
                "name": "Product 2",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute2.id,
                            "value_ids": [(6, 0, attribute2.value_ids.ids)],
                        },
                    )
                ],
                "company_id": False,
            }
        )

        # ACT & ASSERT
        try:
            with self.assertRaises(ValidationError):
                template2.product_variant_ids[0].default_code = "sku4"
                template2.product_variant_ids[1].default_code = "sku3"
                template2.product_variant_ids[2].default_code = "sku2"
        except AssertionError:
            self.fail(
                _(
                    "It has been possible to create a product variant "
                    "when a variant of another template has the same "
                    "Internal Reference"
                )
            )

    def test_09_template_vs_product_dup_archived(self):
        """
        PRE:    - template1 exists
                - template1 has variant11 and variant12 and variant13
                - variant11 has default_code 'sku1'
                - variant12 has default_code 'sku2' and is archived
                - variant13 has default_code 'sku3' and is archived
        ACT:    - change template1 default_code to 'sku1'
        POST:   - template1 is not updated because
                  variant11 has the same default_code 'sku1'
        """
        # ARRANGE
        company1 = self.env["res.company"].create(
            {
                "name": "Company 1",
            }
        )
        attribute1 = self.env["product.attribute"].create(
            {
                "name": "Attribute 1",
                "create_variant": "always",
                "value_ids": [
                    (0, 0, {"name": "Attribute Value 1"}),
                    (0, 0, {"name": "Attribute Value 2"}),
                    (0, 0, {"name": "Attribute Value 3"}),
                ],
            }
        )
        template1 = self.env["product.template"].create(
            {
                "name": "Product 1",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute1.id,
                            "value_ids": [(6, 0, attribute1.value_ids.ids)],
                        },
                    )
                ],
                "company_id": company1.id,
            }
        )
        variant1 = template1.product_variant_ids[0]
        variant2 = template1.product_variant_ids[1]
        variant3 = template1.product_variant_ids[2]

        variant1.default_code = "sku1"
        variant2.default_code = "sku2"
        variant3.default_code = "sku3"

        variant2.active = False
        variant3.active = False

        # ACT & ASSERT
        try:
            with self.assertRaises(ValidationError):
                template1.default_code = "sku1"
        except AssertionError:
            self.fail(
                _(
                    "It has been possible to change the template "
                    "Internal Reference existing a variant with the same one"
                )
            )
