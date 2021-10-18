# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import SavepointCase


class TestAlternateName(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAlternateName, cls).setUpClass()
        cls.project1 = cls.env["project.project"].create(
            {
                "name": "project1",
            }
        )
        cls.attribute1 = cls.env["product.attribute"].create(
            {
                "name": "Color",
            }
        )
        cls.attribute2 = cls.env["product.attribute"].create(
            {
                "name": "Size",
            }
        )
        cls.attribute3 = cls.env["product.attribute"].create(
            {
                "name": "Brand",
            }
        )
        cls.attribute4 = cls.env["product.attribute"].create(
            {
                "name": "Type",
            }
        )
        cls.attribute_value1 = cls.env["product.attribute.value"].create(
            {"name": "white", "attribute_id": cls.attribute1.id}
        )
        cls.attribute_value2 = cls.env["product.attribute.value"].create(
            {"name": "black", "attribute_id": cls.attribute1.id}
        )
        cls.attribute_value3 = cls.env["product.attribute.value"].create(
            {"name": "M", "attribute_id": cls.attribute2.id}
        )
        cls.attribute_value4 = cls.env["product.attribute.value"].create(
            {"name": "XL", "attribute_id": cls.attribute2.id}
        )

        cls.attribute_value5 = cls.env["product.attribute.value"].create(
            {"name": "Special", "attribute_id": cls.attribute3.id}
        )
        cls.attribute_value6 = cls.env["product.attribute.value"].create(
            {"name": "road", "attribute_id": cls.attribute4.id}
        )

        cls.category1 = cls.env["product.category"].create(
            {"name": "Service / Description", "is_service_description": True}
        )

        cls.partner1 = cls.env["res.partner"].create(
            {
                "name": "partner1",
            }
        )
        cls.template1 = cls.env["product.template"].create(
            {
                "name": "product1",
                "type": "service",
                "categ_id": cls.category1.id,
                "service_description_type": "2_color",
                "attribute_line_ids": [
                    (
                        0,
                        False,
                        {
                            "attribute_id": cls.attribute1.id,
                            "value_ids": [(4, cls.attribute_value1.id, False)],
                        },
                    )
                ],
            }
        )

    def test_alternate_name_generator_one_parameter(self):
        """
        PRE:
            - project1 exists
            - attribute_value1 and attribute_value2 exist in attribute1
            - category1 exists
            - partner1 exists
            - template1 has category1
            - template 1 has service_description_type  "2_color"s
        ACT:
            - SaleOrder1 is created
        POST:
            -alternate name is "partner1 white SO*** bring in"
        """
        # ARRANGE:

        # ACT
        saleorder1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner1.id,
                "bike_location": "bring_in",
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": self.template1.product_variant_ids.id,
                        },
                    )
                ],
            }
        )

        # ASSERT
        self.assertEqual(
            saleorder1.alternate_name,
            "partner1 white %s Bring In" % saleorder1.name,
            "Expected 'partner2 white Bring In', %s result found"
            % saleorder1.alternate_name,
        )

    def test_alternate_name_generator_unordered_parameters(self):
        """
        PRE:
            - project1 exists
            - attribute_value1-2 exist in attribute1
            - attribute_value3-4 exist in attribute2
            - attribute_value5 exist in attribute3
            - attribute_value6 exist in attribute4
            - category exists
            - partner1 exists
            - template1-4 has category
            - template 1 has service_description_type  "2_color"
            - template 2 has service_description_type  "3_size"
            - template 3 has service_description_type  "0_brand"
            - template 4 has service_description_type  "1_type"
        ACT:
            - SaleOrder1 is created
        POST:
            -alternate name is "partner1 Special road white XL SO*** bring in"
        """
        # ARRANGE:
        self.template2 = self.env["product.template"].create(
            {
                "name": "product2",
                "type": "service",
                "categ_id": self.category1.id,
                "service_description_type": "3_size",
                "attribute_line_ids": [
                    (
                        0,
                        False,
                        {
                            "attribute_id": self.attribute2.id,
                            "value_ids": [(4, self.attribute_value4.id, False)],
                        },
                    )
                ],
            }
        )
        self.template3 = self.env["product.template"].create(
            {
                "name": "product3",
                "type": "service",
                "categ_id": self.category1.id,
                "service_description_type": "0_brand",
                "attribute_line_ids": [
                    (
                        0,
                        False,
                        {
                            "attribute_id": self.attribute3.id,
                            "value_ids": [(4, self.attribute_value5.id, False)],
                        },
                    )
                ],
            }
        )
        self.template4 = self.env["product.template"].create(
            {
                "name": "product4",
                "type": "service",
                "categ_id": self.category1.id,
                "service_description_type": "1_type",
                "attribute_line_ids": [
                    (
                        0,
                        False,
                        {
                            "attribute_id": self.attribute4.id,
                            "value_ids": [(4, self.attribute_value6.id, False)],
                        },
                    )
                ],
            }
        )

        # ACT
        saleorder1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner1.id,
                "bike_location": "bring_in",
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": self.template1.product_variant_ids.id,
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            "product_id": self.template2.product_variant_ids.id,
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            "product_id": self.template3.product_variant_ids.id,
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            "product_id": self.template4.product_variant_ids.id,
                        },
                    ),
                ],
            }
        )

        # ASSERT
        self.assertEqual(
            saleorder1.alternate_name,
            "partner1 Special road white XL %s Bring In" % saleorder1.name,
            "Expected 'partner1 Special road white XL %s Bring In', %s result found"
            % (saleorder1.name, saleorder1.alternate_name),
        )
