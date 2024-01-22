# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import AbstractComponent, Component


class ProductPricelistItemBatchExporter(AbstractComponent):
    """Export the Oxigesti Product prices.

    For every product in the list, a delayed job is created.
    """

    _name = "oxigesti.product.pricelist.item.batch.exporter"

    def run_common(self, domain=None):
        if not domain:
            domain = []
        # Run the batch synchronization
        parent_domain = domain + [
            ("is_company", "=", True),
            ("customer_rank", ">=", 0),
        ]
        since_date = None
        domain = []
        for e in parent_domain:
            field, operator, value = e
            if field == "write_date":
                since_date = value
            else:
                domain.append(e)
        binder = self.binder_for(self.model._name)
        for p in self.env["res.partner"].search(domain):
            pricelist_items = p.property_product_pricelist.item_ids.filtered(
                lambda x: (
                    not since_date
                    or x.write_date > since_date
                    or p.write_date > since_date
                )
                and x.applied_on == "1_product"
                and x.compute_price == "fixed"
                and (
                    not x.sudo().product_tmpl_id.company_id
                    or x.sudo().product_tmpl_id.company_id == p.company_id
                )
            )
            if pricelist_items:
                # create/update binding data
                for pl in pricelist_items:
                    binding = binder.wrap_binding(
                        pl,
                        binding_extra_vals={
                            "odoo_partner_id": p.id,
                            "deprecated": pl.is_deprecated(p),
                        },
                    )
                    self._export_record(binding)


class ProductPricelistItemDelayedBatchExporter(Component):
    """Export the Oxigesti Product prices.

    For every product in the list, a delayed job is created.
    """

    _name = "oxigesti.product.pricelist.item.delayed.batch.exporter"
    _inherit = [
        "oxigesti.delayed.batch.exporter",
        "oxigesti.product.pricelist.item.batch.exporter",
    ]

    def run(self, domain=None):
        super().run_common(domain=domain)


class ProductPricelistItemDirectBatchExporter(Component):
    """Export the Oxigesti Product prices.

    For every product in the list, a direct job is created.
    """

    _name = "oxigesti.product.pricelist.item.direct.batch.exporter"
    _inherit = [
        "oxigesti.direct.batch.exporter",
        "oxigesti.product.pricelist.item.batch.exporter",
    ]

    def run(self, domain=None):
        super().run_common(domain=domain)


class ProductPricelistItemExporter(Component):
    _name = "oxigesti.product.pricelist.item.exporter"
    _inherit = "oxigesti.exporter"

    _apply_on = "oxigesti.product.pricelist.item"

    def _export_dependencies(self):
        # partner
        binder = self.binder_for("oxigesti.res.partner")
        binding_model = binder.model._name
        odoo_partner_id = self.binding.with_context(active_test=False).odoo_partner_id
        external_id = binder.to_external(odoo_partner_id, wrap=True)
        if external_id:
            self._import_dependency(external_id, binding_model, always=False)
        else:
            importer = self.component(
                usage="direct.batch.importer", model_name=binding_model
            )
            importer.run(
                filters=[
                    (
                        "Codigo_Cliente_Logic",
                        "=",
                        odoo_partner_id.ref
                        and odoo_partner_id.ref.strip()
                        and odoo_partner_id.ref
                        or None,
                    ),
                ]
            )

        # product
        binder = self.binder_for("oxigesti.product.product")
        relation = self.binding.with_context(
            active_test=False
        ).product_tmpl_id.product_variant_id
        if not binder.to_external(relation, wrap=True):
            exporter = self.component(
                usage="record.exporter", model_name=binder.model._name
            )
            exporter.run(relation)
