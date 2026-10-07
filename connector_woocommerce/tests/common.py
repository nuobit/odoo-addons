# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta
from unittest.mock import patch

from freezegun import freeze_time

from odoo.modules.graph import Graph
from odoo.modules.migration import MigrationManager
from odoo.modules.module import load_information_from_description_file
from odoo.tests import Form

from odoo.addons.component.tests.common import SavepointComponentCase

# What the HTML editor leaves in a field nobody typed in, a real text with a
# colour the export converts, and that text as WooCommerce receives it.
PLACEHOLDER = "<p><br></p>"
TEXT = '<p style="color: rgb(255, 0, 0);">Real text</p>'
TEXT_HEX = '<p style="color: #FF0000;">Real text</p>'


class BlankHtmlMigrationMixin:
    """Run the real migration and inspect the jobs of the two export buttons."""

    def setUp(self):
        super().setUp()
        freezer = freeze_time("2030-01-01 12:00:00")
        self.clock = freezer.start()
        self.addCleanup(freezer.stop)

    def _start_incremental_exports(self):
        self.env["product.template"].flush()
        self.env["product.product"].flush()
        self.clock.tick(timedelta(seconds=1))
        self.backend.export_product_tmpl_since()
        self.backend.export_products_since()
        self.clock.tick(timedelta(seconds=1))

    def _assert_export_selection(self, binding_model, action, expected):
        jobs = self.env["queue.job"]
        domain = [
            ("model_name", "=", binding_model),
            ("method_name", "=", "export_batch"),
        ]
        before = jobs.search(domain)
        action()
        created = jobs.search(domain) - before
        self.assertEqual(len(created), 1)
        selected = (
            self.env[expected._name]
            .with_context(active_test=False)
            .search(created.kwargs["domain"])
        )
        self.assertEqual(selected.sorted("id"), expected.sorted("id"))


class WooCommerceCase(SavepointComponentCase):
    """Backend, discount pricelist and bound products without any HTTP call."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._write_dates = {}
        cls.langs = cls._setup_languages()
        cls.discount_pricelist = cls.env["product.pricelist"].create(
            {"name": "WooCommerce discount pricelist"}
        )
        cls.other_pricelist = cls.env["product.pricelist"].create(
            {"name": "Other pricelist"}
        )
        cls.backend = cls.env["woocommerce.backend"].create(
            {
                "name": "WooCommerce test backend",
                "url": "http://127.0.0.1:1",
                "consumer_key": "ck_test",
                "consumer_secret": "cs_test",
                "lang_ids": [(6, 0, cls.langs.ids)],
                "language_id": cls.langs[0].id,
                "client_order_ref_prefix": "WC",
                "stock_location_ids": [
                    (6, 0, cls.env.ref("stock.stock_location_stock").ids)
                ],
                "discount_pricelist_id": cls.discount_pricelist.id,
            }
        )
        cls.category = cls.env["product.category"].create(
            {"name": "WooCommerce test category"}
        )
        cls.template = cls._create_template("WooCommerce bound product", 1001)
        cls.unbound_template = cls._create_template("WooCommerce unbound product")

    @classmethod
    def _setup_languages(cls):
        """The export languages of the backend, the default one first."""
        return cls.env.ref("base.lang_en")

    @classmethod
    def _create_template(cls, name, woocommerce_idproduct=None, list_price=100.0):
        template = cls.env["product.template"].create(
            {
                "name": name,
                "list_price": list_price,
                "categ_id": cls.category.id,
                "woocommerce_enabled": True,
            }
        )
        if woocommerce_idproduct:
            cls.env["woocommerce.product.template"].create(
                cls._template_binding_values(template, woocommerce_idproduct)
            )
        cls._remember_write_dates(template)
        return template

    @classmethod
    def _template_binding_values(cls, template, woocommerce_idproduct):
        return {
            "odoo_id": template.id,
            "backend_id": cls.backend.id,
            "woocommerce_idproduct": woocommerce_idproduct,
        }

    @classmethod
    def _bind_variant(cls, variant, woocommerce_idproduct):
        return cls.env["woocommerce.product.product"].create(
            cls._variant_binding_values(variant, woocommerce_idproduct)
        )

    @classmethod
    def _variant_binding_values(cls, variant, woocommerce_idproduct):
        return {
            "odoo_id": variant.id,
            "backend_id": cls.backend.id,
            "woocommerce_idproduct": woocommerce_idproduct,
            "woocommerce_idparent": woocommerce_idproduct + 1,
        }

    def _create_variable_template(self):
        attribute = self.env["product.attribute"].create({"name": "Size"})
        values = self.env["product.attribute.value"].create(
            [
                {"name": "Small", "attribute_id": attribute.id},
                {"name": "Large", "attribute_id": attribute.id},
            ]
        )
        self.env["woocommerce.product.attribute"].create(
            {
                "odoo_id": attribute.id,
                "backend_id": self.backend.id,
                "woocommerce_idattribute": 3001,
            }
        )
        template = self._create_template("Variable product", 1003)
        template.write(
            {
                "taxes_id": [(5, 0, 0)],
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, values.ids)],
                        },
                    ),
                ],
            }
        )
        return template

    def _mapped_values(self, model_name, product):
        with self.backend.work_on(model_name) as work:
            mapper = work.component(usage="export.mapper")
            # The exporter maps the actual product, not its binding.
            return mapper.map_record(product).values()

    def _export_payload(self, model_name, product, external_id):
        data = self._mapped_values(model_name, product)
        with self.backend.work_on(model_name) as work:
            adapter = work.component(usage="backend.adapter")
            # Stop only at the external API boundary; run real formatting.
            with patch.object(type(adapter), "_exec", return_value={}) as call:
                adapter.write(external_id, data)
            call.assert_called_once()
            args, kwargs = call.call_args
            self.assertEqual(args[0], "put")
            return kwargs["data"]

    def _run_migration(self, module, target_version, installed_version):
        graph = Graph()
        module_info = load_information_from_description_file(module)
        package = graph.add_node(module, {**module_info, "version": target_version})
        graph.update_from_db(self.env.cr)
        # Describe an upgrade even when this suite runs during a fresh install.
        # Change only the graph node, not the installed module record: the real
        # manager skips nodes that retain the "to install" state.
        package.installed_version = installed_version
        package.state = "to upgrade"
        package.update = True
        MigrationManager(self.env.cr, graph).migrate_module(package, "post")

    @classmethod
    def _remember_write_dates(cls, template):
        variants = template.with_context(active_test=False).product_variant_ids
        for records in (template, variants):
            for record in records:
                cls._write_dates[
                    record._name, record.id
                ] = record.woocommerce_write_date

    def _create_rule(self, pricelist=None, **values):
        vals = {
            "pricelist_id": (pricelist or self.discount_pricelist).id,
            "applied_on": "1_product",
            "product_tmpl_id": self.template.id,
            "compute_price": "fixed",
            "fixed_price": 80.0,
        }
        vals.update(values)
        return self.env["product.pricelist.item"].create(vals)

    def _translate(self, record, field_name, value):
        """Save the Spanish translation of a field without writing the record
        it translates, as the translation dialog does. The test class
        activates Spanish."""
        return self.env["ir.translation"].create(
            {
                "type": "model",
                "name": "%s,%s" % (record._name, field_name),
                "res_id": record.id,
                "lang": "es_ES",
                "src": record[field_name],
                "value": value,
                "state": "translated",
            }
        )

    def assert_touched(self, records):
        for record in records:
            self.assertNotEqual(
                record.woocommerce_write_date,
                self._write_dates[record._name, record.id],
                "%s should have been marked for export" % record.display_name,
            )

    def assert_untouched(self, records):
        for record in records:
            self.assertEqual(
                record.woocommerce_write_date,
                self._write_dates[record._name, record.id],
                "%s should not have been marked for export" % record.display_name,
            )

    def _new_jobs(self, model_name, method_name, run):
        """The ``method_name`` jobs of ``model_name`` that ``run`` queues."""
        job_model = self.env["queue.job"]
        domain = [("model_name", "=", model_name), ("method_name", "=", method_name)]
        # A request flushes when it ends, and the computations it runs then may
        # queue jobs: flushing on both sides counts the jobs of ``run`` alone.
        self.env["base"].flush()
        before = job_model.search(domain)
        run()
        self.env["base"].flush()
        return job_model.search(domain) - before

    def _new_job(self, model_name, method_name, run):
        jobs = self._new_jobs(model_name, method_name, run)
        self.assertEqual(len(jobs), 1)
        return jobs


class WooCommerceOrderCase(WooCommerceCase):
    """Shop orders of storable products, taken through the delivery flow."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "WooCommerce customer"})
        cls.product_1 = cls._create_storable_product("WooCommerce product 1")
        cls.product_2 = cls._create_storable_product("WooCommerce product 2")
        cls.product_3 = cls._create_storable_product("WooCommerce product 3")

    @classmethod
    def _create_storable_product(cls, name):
        product = cls.env["product.product"].create({"name": name, "type": "product"})
        cls.env["stock.quant"]._update_available_quantity(
            product, cls.env.ref("stock.stock_location_stock"), 100.0
        )
        return product

    def _create_order(self, quantities):
        """A shop order as the import creates it, with ``quantities`` by product."""
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "is_woocommerce": True,
                "order_line": [
                    (0, 0, {"product_id": product.id, "product_uom_qty": quantity})
                    for product, quantity in quantities.items()
                ],
            }
        )

    def _bind_order(self, order, woocommerce_idsaleorder):
        return self.env["woocommerce.sale.order"].create(
            {
                "odoo_id": order.id,
                "backend_id": self.backend.id,
                "woocommerce_idsaleorder": woocommerce_idsaleorder,
                "woocommerce_status": "processing",
            }
        )

    def _validate(self, picking, quantities=None, backorder=True):
        """Validate ``picking`` as the user does: the done ``quantities`` by
        product, everything by default, and ``backorder`` as the answer to the
        backorder question when something is left."""
        picking.action_assign()
        for move in picking.move_lines:
            move.quantity_done = (
                quantities.get(move.product_id, 0.0)
                if quantities is not None
                else move.product_uom_qty
            )
        action = picking.button_validate()
        if action is not True:
            self.assertEqual(action["res_model"], "stock.backorder.confirmation")
            wizard = Form(
                self.env[action["res_model"]].with_context(action["context"])
            ).save()
            if backorder:
                wizard.process()
            else:
                wizard.process_cancel_backorder()

    def _create_return(self, picking, quantities=None, to_refund=True):
        """Return ``picking`` as the user does with the return wizard: the
        ``quantities`` by product, everything by default, and ``to_refund`` as
        the «Update quantities on SO/PO» answer. The return is left open."""
        wizard = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.id,
                active_model="stock.picking",
            )
        ).save()
        for line in wizard.product_return_moves:
            if quantities is not None:
                line.quantity = quantities.get(line.product_id, 0.0)
            line.to_refund = to_refund
        action = wizard.create_returns()
        return self.env["stock.picking"].browse(action["res_id"])
