# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from .common import WooCommerceCase


class TestCategoryDependencyExport(WooCommerceCase):
    def test_product_export_creates_its_new_category_after_the_parent(self):
        parent = self.env["product.public.category"].create(
            {"name": "Respiratory", "slug_name": "respiratory"}
        )
        category = self.env["product.public.category"].create(
            {"name": "Masks", "slug_name": "masks", "parent_id": parent.id}
        )
        template = self._create_template("Mask")
        template.public_categ_ids = category
        created = []

        def shop(op, resource, *args, **kwargs):
            # The shop has no category yet: a search finds nothing, and each
            # create answers with the next shop id
            if op == "get":
                return []
            created.append((op, resource, kwargs["data"]))
            return {**kwargs["data"], "id": 3000 + len(created)}

        with self.backend.work_on("woocommerce.product.public.category") as work:
            adapter = work.component(usage="backend.adapter")
            # Stop only at the external API boundary; run the real exporters
            with patch.object(type(adapter), "_exec", side_effect=shop):
                with self.backend.work_on("woocommerce.product.template") as work:
                    exporter = work.component(usage="record.direct.exporter")
                    exporter._export_dependencies(template)
        self.assertEqual(
            [
                (op, resource, data["name"], data.get("parent"))
                for op, resource, data in created
            ],
            [
                ("post", "products/categories", "Respiratory", None),
                ("post", "products/categories", "Masks", 3001),
            ],
        )
        self.assertEqual(parent.woocommerce_bind_ids.woocommerce_idpubliccategory, 3001)
        self.assertEqual(
            category.woocommerce_bind_ids.woocommerce_idpubliccategory, 3002
        )
