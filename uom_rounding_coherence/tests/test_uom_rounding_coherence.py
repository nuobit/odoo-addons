# Copyright 2026 NuoBiT Solutions SL- Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo  <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestUomRoundingCoherence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["uom.category"].create(
            {"name": "Test Coherence Category"}
        )
        cls.ref_uom = cls.env["uom.uom"].create(
            {
                "name": "Ref Unit",
                "category_id": cls.category.id,
                "uom_type": "reference",
                "rounding": 0.001,
            }
        )

    def test_coherent_rounding_passes(self):
        """
        PRE:    - A reference UoM exists with rounding 0.001
        ACT:    - Create a smaller UoM with factor=1.141 and rounding=0.001
        POST:   - The UoM is created without error because
                  effective rounding (0.001 / 1.141 ≈ 0.000877) <= ref rounding (0.001)
        """
        # ARRANGE & ACT
        self.env["uom.uom"].create(
            {
                "name": "Fine Unit",
                "category_id": self.category.id,
                "uom_type": "smaller",
                "factor": 1.141,
                "rounding": 0.001,
            }
        )

    def test_coarse_rounding_fails(self):
        """
        PRE:    - A reference UoM exists with rounding 0.001
        ACT:    - Create a smaller UoM with factor=1.141 and rounding=0.01
        POST:   - ValidationError is raised because
                  effective rounding (0.01 / 1.141 ≈ 0.00877) > ref rounding (0.001)
        """
        # ARRANGE & ACT & ASSERT
        with self.assertRaises(ValidationError):
            self.env["uom.uom"].create(
                {
                    "name": "Coarse Unit",
                    "category_id": self.category.id,
                    "uom_type": "smaller",
                    "factor": 1.141,
                    "rounding": 0.01,
                }
            )

    def test_borderline_rounding_passes(self):
        """
        PRE:    - A reference UoM exists with rounding 0.0001
        ACT:    - Create a smaller UoM with factor=0.8086 and rounding=0.0001
        POST:   - The UoM is created without error because
                  effective rounding (0.0001 / 0.8086 ≈ 0.0001237) is within
                  float_compare tolerance of ref rounding (0.0001)
        """
        # ARRANGE
        category = self.env["uom.category"].create({"name": "Test Borderline Category"})
        self.env["uom.uom"].create(
            {
                "name": "Ref Borderline",
                "category_id": category.id,
                "uom_type": "reference",
                "rounding": 0.0001,
            }
        )
        # ACT
        self.env["uom.uom"].create(
            {
                "name": "Borderline Unit",
                "category_id": category.id,
                "uom_type": "smaller",
                "factor": 0.8086,
                "rounding": 0.0001,
            }
        )

    def test_update_rounding_to_coarse_fails(self):
        """
        PRE:    - A reference UoM exists with rounding 0.001
                - A smaller UoM exists with factor=1.141 and rounding=0.001
        ACT:    - Update the smaller UoM rounding to 0.01
        POST:   - ValidationError is raised because
                  effective rounding (0.01 / 1.141 ≈ 0.00877) > ref rounding (0.001)
        """
        # ARRANGE
        uom = self.env["uom.uom"].create(
            {
                "name": "Update Test Unit",
                "category_id": self.category.id,
                "uom_type": "smaller",
                "factor": 1.141,
                "rounding": 0.001,
            }
        )
        # ACT & ASSERT
        with self.assertRaises(ValidationError):
            uom.write({"rounding": 0.01})

    def test_update_ref_rounding_to_finer_fails(self):
        """
        PRE:    - A reference UoM exists with rounding 0.01
                - A smaller UoM exists with factor=1.141 and rounding=0.01
                  (effective rounding 0.01 / 1.141 ≈ 0.00877 <= 0.01: OK)
        ACT:    - Update the reference UoM rounding to 0.001
        POST:   - ValidationError is raised because
                  effective rounding (0.01 / 1.141 ≈ 0.00877) > new ref rounding (0.001)
        """
        # ARRANGE
        category = self.env["uom.category"].create({"name": "Test Ref Update Category"})
        ref = self.env["uom.uom"].create(
            {
                "name": "Ref Updatable",
                "category_id": category.id,
                "uom_type": "reference",
                "rounding": 0.01,
            }
        )
        self.env["uom.uom"].create(
            {
                "name": "Secondary",
                "category_id": category.id,
                "uom_type": "smaller",
                "factor": 1.141,
                "rounding": 0.01,
            }
        )
        # ACT & ASSERT
        with self.assertRaises(ValidationError):
            ref.write({"rounding": 0.001})

    def test_bigger_uom_coarse_rounding_fails(self):
        """
        PRE:    - A reference UoM exists with rounding 0.001
        ACT:    - Create a bigger UoM with factor=0.001 and rounding=1.0
        POST:   - ValidationError is raised because
                  effective rounding (1.0 / 0.001 = 1000) >> ref rounding (0.001)
        """
        # ARRANGE & ACT & ASSERT
        with self.assertRaises(ValidationError):
            self.env["uom.uom"].create(
                {
                    "name": "Big Coarse Unit",
                    "category_id": self.category.id,
                    "uom_type": "bigger",
                    "factor": 0.001,
                    "rounding": 1.0,
                }
            )

    def test_bigger_uom_coherent_rounding_passes(self):
        """
        PRE:    - A reference UoM exists with rounding 0.001
        ACT:    - Create a bigger UoM with factor=0.001 and rounding=0.000001
        POST:   - The UoM is created without error because
                  effective rounding (0.000001 / 0.001 = 0.001) <= ref rounding (0.001)
        """
        # ARRANGE & ACT
        self.env["uom.uom"].create(
            {
                "name": "Big Fine Unit",
                "category_id": self.category.id,
                "uom_type": "bigger",
                "factor": 0.001,
                "rounding": 0.000001,
            }
        )

    def test_bigger_uom_integer_ratio_passes(self):
        """
        PRE:    - A reference UoM exists with rounding 0.001
        ACT:    - Create a bigger UoM with factor=1/12 (dozen) and rounding=0.00001
        POST:   - The UoM is created without error because
                  effective rounding
                  (0.00001 / 0.08333 ≈ 0.00012) <= ref rounding (0.001)
        """
        # ARRANGE & ACT
        self.env["uom.uom"].create(
            {
                "name": "Dozen",
                "category_id": self.category.id,
                "uom_type": "bigger",
                "factor": 0.08333333333,  # 1/12
                "rounding": 0.00001,
            }
        )

    def test_reference_only_category_passes(self):
        """
        PRE:    - A category exists with only a reference UoM
        ACT:    - Update the reference UoM rounding
        POST:   - No error is raised because there are no non-reference
                  UoMs to validate against
        """
        # ARRANGE
        category = self.env["uom.category"].create(
            {"name": "Test Reference Only Category"}
        )
        ref = self.env["uom.uom"].create(
            {
                "name": "Ref Only",
                "category_id": category.id,
                "uom_type": "reference",
                "rounding": 0.01,
            }
        )
        # ACT
        ref.write({"rounding": 0.001})

    def test_no_active_reference_uom_fails(self):
        """
        PRE:    - A category exists with a reference UoM and a smaller UoM
        ACT:    - Archive the reference UoM via SQL (bypassing ORM constraints)
                  and update the non-reference UoM rounding to trigger validation
        POST:   - ValidationError is raised because no active reference UoM
                  is found to validate against
        """
        # ARRANGE
        category = self.env["uom.category"].create(
            {"name": "Test No Active Ref Category"}
        )
        ref = self.env["uom.uom"].create(
            {
                "name": "Ref To Deactivate",
                "category_id": category.id,
                "uom_type": "reference",
                "rounding": 0.001,
            }
        )
        non_ref = self.env["uom.uom"].create(
            {
                "name": "Orphan Unit",
                "category_id": category.id,
                "uom_type": "smaller",
                "factor": 2.0,
                "rounding": 0.001,
            }
        )
        self.env.cr.execute(
            "UPDATE uom_uom SET active = FALSE WHERE id = %s", (ref.id,)
        )
        self.env["uom.uom"].invalidate_model()
        # ACT & ASSERT
        with self.assertRaises(ValidationError):
            non_ref.write({"rounding": 0.0001})

    def test_multiple_active_reference_uoms_fails(self):
        """
        PRE:    - A category exists with a reference UoM and two smaller UoMs
        ACT:    - Change one smaller UoM to reference type via SQL
                  (bypassing ORM constraints) and update the other smaller
                  UoM rounding to trigger validation
        POST:   - ValidationError is raised because multiple active reference
                  UoMs are found
        """
        # ARRANGE
        category = self.env["uom.category"].create({"name": "Test Multi Ref Category"})
        self.env["uom.uom"].create(
            {
                "name": "Ref Original",
                "category_id": category.id,
                "uom_type": "reference",
                "rounding": 0.001,
            }
        )
        to_corrupt = self.env["uom.uom"].create(
            {
                "name": "Unit To Corrupt",
                "category_id": category.id,
                "uom_type": "smaller",
                "factor": 2.0,
                "rounding": 0.001,
            }
        )
        another = self.env["uom.uom"].create(
            {
                "name": "Another Unit",
                "category_id": category.id,
                "uom_type": "smaller",
                "factor": 3.0,
                "rounding": 0.001,
            }
        )
        self.env.cr.execute(
            "UPDATE uom_uom SET uom_type = 'reference', factor = 1.0 WHERE id = %s",
            (to_corrupt.id,),
        )
        self.env["uom.uom"].invalidate_model()
        # ACT & ASSERT
        with self.assertRaises(ValidationError):
            another.write({"rounding": 0.0001})

    def _create_product_with_uom(self, name, uom):
        """Create a storable product via SQL to avoid NOT NULL issues
        from optional modules (sale, purchase) adding required columns."""
        self.env.cr.execute(
            """
            INSERT INTO product_template
                (name, type, uom_id, uom_po_id, categ_id, active,
                 sale_ok, purchase_ok, list_price, tracking,
                 sale_line_warn, purchase_line_warn,
                 create_uid, write_uid, create_date, write_date)
            VALUES
                (%s, 'product', %s, %s, 1, true,
                 false, false, 0, 'none',
                 'no-message', 'no-message',
                 1, 1, now() at time zone 'UTC', now() at time zone 'UTC')
            RETURNING id
            """,
            (name, uom.id, uom.id),
        )
        tmpl_id = self.env.cr.fetchone()[0]
        self.env.cr.execute(
            """
            INSERT INTO product_product
                (product_tmpl_id, active, default_code,
                 create_uid, write_uid, create_date, write_date)
            VALUES
                (%s, true, NULL, 1, 1,
                 now() at time zone 'UTC', now() at time zone 'UTC')
            RETURNING id
            """,
            (tmpl_id,),
        )
        product_id = self.env.cr.fetchone()[0]
        return self.env["product.product"].browse(product_id)

    def test_coarser_rounding_blocked_by_existing_quants(self):
        """
        PRE:    - A product exists with a UoM that has rounding=0.001
                - A stock quant exists with quantity=5825.949 (3 decimals)
        ACT:    - Change the UoM rounding to 0.01 (2 decimals)
        POST:   - ValidationError is raised because the quant value 5825.949
                  has more decimals than the new rounding allows
        """
        # ARRANGE
        category = self.env["uom.category"].create(
            {"name": "Test Quant Coherence Category"}
        )
        uom = self.env["uom.uom"].create(
            {
                "name": "Quant Test Unit",
                "category_id": category.id,
                "uom_type": "reference",
                "rounding": 0.001,
            }
        )
        product = self._create_product_with_uom("Quant Test Product", uom)
        location = self.env.ref("stock.stock_location_stock")
        self.env["stock.quant"].create(
            {
                "product_id": product.id,
                "location_id": location.id,
                "quantity": 5825.949,
            }
        )
        # ACT & ASSERT
        with self.assertRaises(ValidationError):
            uom.write({"rounding": 0.01})

    def test_finer_rounding_allowed_with_existing_quants(self):
        """
        PRE:    - A product exists with a UoM that has rounding=0.01
                - A stock quant exists with quantity=5825.95 (2 decimals)
        ACT:    - Change the UoM rounding to 0.001 (3 decimals)
        POST:   - No error is raised because 5825.95 fits within 0.001
        """
        # ARRANGE
        category = self.env["uom.category"].create(
            {"name": "Test Finer Rounding Category"}
        )
        uom = self.env["uom.uom"].create(
            {
                "name": "Finer Test Unit",
                "category_id": category.id,
                "uom_type": "reference",
                "rounding": 0.01,
            }
        )
        product = self._create_product_with_uom("Finer Test Product", uom)
        location = self.env.ref("stock.stock_location_stock")
        self.env["stock.quant"].create(
            {
                "product_id": product.id,
                "location_id": location.id,
                "quantity": 5825.95,
            }
        )
        # ACT — should not raise
        uom.write({"rounding": 0.001})
