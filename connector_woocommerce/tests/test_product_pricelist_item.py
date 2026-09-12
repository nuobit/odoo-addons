# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from freezegun import freeze_time

from .common import WooCommerceCase


class TestProductPricelistItem(WooCommerceCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.second_template = cls._create_template("Second bound product", 1002)
        cls.child_category = cls.env["product.category"].create(
            {"name": "Child category", "parent_id": cls.category.id}
        )
        cls.child_template = cls._create_template("Child category product", 1003)
        cls.child_template.categ_id = cls.child_category
        cls.variable_template = cls._create_template("Variable product", 1004)
        attribute = cls.env["product.attribute"].create({"name": "Size"})
        values = cls.env["product.attribute.value"].create(
            [
                {"name": "Small", "attribute_id": attribute.id},
                {"name": "Large", "attribute_id": attribute.id},
            ]
        )
        cls.variable_template.write(
            {
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, values.ids)],
                        },
                    )
                ]
            }
        )
        for index, variant in enumerate(cls.variable_template.product_variant_ids):
            cls._bind_variant(variant, 2001 + index)
        cls.templates = (
            cls.template
            | cls.unbound_template
            | cls.second_template
            | cls.child_template
            | cls.variable_template
        )

    def setUp(self):
        super().setUp()
        self._remember_write_dates(self.templates)
        freezer = freeze_time("2030-01-01 12:00:00")
        self.clock = freezer.start()
        self.addCleanup(freezer.stop)

    def _next_change(self):
        self._remember_write_dates(self.templates)
        self.clock.tick(timedelta(seconds=1))

    def test_create_marks_simple_template_and_its_variant(self):
        self._create_rule()
        self.assert_touched(self.template)
        self.assert_touched(self.template.product_variant_ids)
        self.assert_untouched(self.unbound_template | self.second_template)

    def test_price_and_validity_edits_mark_template(self):
        rule = self._create_rule()
        changes = [
            {"fixed_price": 75.0},
            {"date_start": "2030-01-01 00:00:00"},
            {"date_end": "2030-02-01 00:00:00"},
            {"min_quantity": 2.0},
            {"compute_price": "percentage"},
            {"percent_price": 25.0},
            {"compute_price": "formula"},
            {"price_discount": 20.0},
            {"price_surcharge": 2.0},
            {"price_round": 0.5},
            {"price_max_margin": 10.0},
            {"price_min_margin": 1.0},
            {"base_pricelist_id": self.other_pricelist.id},
            {"base": "pricelist"},
        ]
        for values in changes:
            with self.subTest(values=values):
                self._next_change()
                rule.write(values)
                self.assert_touched(self.template)
                self.assert_untouched(self.unbound_template | self.second_template)

    def test_moving_template_marks_old_and_new_products(self):
        rule = self._create_rule()
        self._next_change()
        rule.product_tmpl_id = self.second_template
        self.assert_touched(self.template | self.second_template)
        self.assert_untouched(self.unbound_template)

    def test_moving_variant_marks_old_and_new_variants(self):
        variants = self.variable_template.product_variant_ids.sorted("id")
        first, second = variants
        rule = self._create_rule(
            applied_on="0_product_variant",
            product_tmpl_id=False,
            product_id=first.id,
        )
        self._next_change()
        rule.product_id = second
        self.assert_touched(variants)
        self.assert_touched(self.variable_template)
        self.assert_untouched(self.template)

    def test_variant_rule_on_simple_product_marks_its_template(self):
        variant = self.template.product_variant_id
        self._create_rule(
            applied_on="0_product_variant", product_tmpl_id=False, product_id=variant.id
        )
        self.assert_touched(self.template)
        self.assert_touched(variant)
        self.assert_untouched(self.unbound_template | self.second_template)

    def test_moving_pricelist_marks_leaving_and_entering_discount_list(self):
        rule = self._create_rule()
        self._next_change()
        rule.pricelist_id = self.other_pricelist
        self.assert_touched(self.template)
        self._next_change()
        rule.pricelist_id = self.discount_pricelist
        self.assert_touched(self.template)

    def test_template_rule_marks_archived_bound_variants(self):
        variants = self.variable_template.product_variant_ids.sorted("id")
        first, second = variants
        first.action_archive()
        self._next_change()
        self._create_rule(product_tmpl_id=self.variable_template.id)
        self.assert_touched(self.variable_template)
        self.assert_touched(first | second)
        self.assert_untouched(self.template)

    def test_category_rule_includes_descendants_and_only_bound_records(self):
        self._create_rule(
            applied_on="2_product_category",
            product_tmpl_id=False,
            categ_id=self.category.id,
        )
        bound_templates = self.templates - self.unbound_template
        self.assert_touched(bound_templates)
        self.assert_touched(bound_templates.product_variant_ids)
        self.assert_untouched(self.unbound_template)
        self.assert_untouched(self.unbound_template.product_variant_ids)

    def test_moving_category_marks_previous_and_new_subtrees(self):
        other_category = self.env["product.category"].create({"name": "Other category"})
        self.second_template.categ_id = other_category
        rule = self._create_rule(
            applied_on="2_product_category",
            product_tmpl_id=False,
            categ_id=self.child_category.id,
        )
        self._next_change()
        rule.categ_id = other_category
        self.assert_touched(self.child_template | self.second_template)
        self.assert_untouched(self.template | self.unbound_template)

    def test_global_rule_marks_all_bound_templates_and_variants(self):
        self._create_rule(applied_on="3_global", product_tmpl_id=False)
        bound_templates = self.templates - self.unbound_template
        self.assert_touched(bound_templates)
        self.assert_touched(bound_templates.product_variant_ids)
        self.assert_untouched(self.unbound_template)
        self.assert_untouched(self.unbound_template.product_variant_ids)

    def test_rule_on_another_pricelist_does_not_mark_products(self):
        self._create_rule(pricelist=self.other_pricelist)
        self.assert_untouched(self.templates)
        self.assert_untouched(self.templates.product_variant_ids)

    def test_editing_or_removing_base_list_rules_marks_dependent_products(self):
        base_rule = self._create_rule(pricelist=self.other_pricelist)
        self._create_rule(
            compute_price="formula",
            base="pricelist",
            base_pricelist_id=self.other_pricelist.id,
        )
        self._next_change()
        base_rule.fixed_price = 70.0
        self.assert_touched(self.template)
        self._next_change()
        base_rule.unlink()
        self.assert_touched(self.template)
        self.assert_untouched(self.unbound_template | self.second_template)

    def test_archiving_and_restoring_base_pricelist_marks_dependent_products(self):
        self._create_rule(pricelist=self.other_pricelist)
        self._create_rule(
            compute_price="formula",
            base="pricelist",
            base_pricelist_id=self.other_pricelist.id,
        )
        self._next_change()
        self.other_pricelist.action_archive()
        self.assert_touched(self.template)
        self._next_change()
        self.other_pricelist.action_unarchive()
        self.assert_touched(self.template)

    def test_changing_scope_marks_previous_and_new_targets(self):
        rule = self._create_rule()
        self._next_change()
        rule.write({"applied_on": "3_global", "product_tmpl_id": False})
        self.assert_touched(self.templates - self.unbound_template)
        self.assert_untouched(self.unbound_template)

    def test_batch_create_and_write_handle_multiple_rules(self):
        rules = self.env["product.pricelist.item"].create(
            [
                {
                    "pricelist_id": self.discount_pricelist.id,
                    "applied_on": "1_product",
                    "product_tmpl_id": template.id,
                    "fixed_price": 70.0,
                }
                for template in self.template | self.second_template
            ]
        )
        self.assert_touched(self.template | self.second_template)
        self._next_change()
        rules.write({"fixed_price": 65.0})
        self.assert_touched(self.template | self.second_template)
        self.assert_untouched(self.unbound_template)

    def test_deleting_rules_marks_all_previous_targets(self):
        rules = self._create_rule() | self._create_rule(
            product_tmpl_id=self.variable_template.id
        )
        self._next_change()
        rules.unlink()
        self.assert_touched(self.template | self.variable_template)
        self.assert_touched(self.variable_template.product_variant_ids)
        self.assert_untouched(self.unbound_template)

    def test_archiving_and_restoring_discount_pricelist_marks_bound_products(self):
        self._create_rule()
        self._next_change()
        self.discount_pricelist.action_archive()
        self.assert_touched(self.template)
        self._next_change()
        self.discount_pricelist.action_unarchive()
        self.assert_touched(self.template)

    def test_empty_rule_operations_do_not_mark_products(self):
        rules = self.env["product.pricelist.item"]
        rules.write({"fixed_price": 50.0})
        rules.unlink()
        self.assert_untouched(self.templates)
