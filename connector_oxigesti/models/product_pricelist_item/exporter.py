# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component

# class ProductPricelistItemBatchExporter(AbstractComponent):
#     """Export the Oxigesti Product prices.
#
#     For every product in the list, a delayed job is created.
#     """
#
#     _name = "oxigesti.product.pricelist.item.batch.exporter"
#
#     def run_common(self, domain=None):
#         if not domain:
#             domain = []
#         # Run the batch synchronization
#         parent_domain = domain + [
#             ("is_company", "=", True),
#             ("customer_rank", ">=", 0),
#         ]
#         since_date = None
#         domain = []
#         for e in parent_domain:
#             field, operator, value = e
#             if field == "write_date":
#                 since_date = value
#             else:
#                 domain.append(e)
#         partner_adapter = self.component(
#             usage="backend.adapter", model_name="oxigesti.res.partner"
#         )
#         partner_binder = self.binder_for("oxigesti.res.partner")
#         binder = self.binder_for(self.model._name)
#         for p in self.env["res.partner"].search(domain):
#             pricelist_items = p.property_product_pricelist.item_ids.filtered(
#                 lambda x: (
#                     not since_date
#                     or x.write_date > since_date
#                     or p.write_date > since_date
#                 )
#                 and x.applied_on == "1_product"
#                 and x.compute_price == "fixed"
#                 and (
#                     not x.sudo().product_tmpl_id.company_id
#                     or x.sudo().product_tmpl_id.company_id == p.company_id
#                 )
#             )
#             if pricelist_items:
#                 # create/update binding data
#                 partner_external_id = partner_binder.to_external(p, wrap=True)
#                 for pl in pricelist_items:
#                     if pl.product_tmpl_id.default_code and partner_external_id:
#                         external_id = [
#                             pl.product_tmpl_id.default_code,
#                             partner_adapter.id2dict(partner_external_id)[
#                                 "Codigo_Mutua"
#                             ],
#                         ]
#                         binding = binder.to_internal(external_id)
#                         if binding and binding.odoo_id != pl:
#                             old_binding = binder._find_binding(
#                                 pl, binding_extra_vals={"odoo_partner_id": p.id}
#                             )
#                             if old_binding:
#                                 old_binding.unlink()
#                             binding.odoo_id = pl
#                     binding = binder.wrap_binding(
#                         pl,
#                         binding_extra_vals={
#                             "odoo_partner_id": p.id,
#                             "deprecated": pl.is_deprecated(p),
#                         },
#                     )
#                     self._export_record(binding)


class ProductPricelistItemDelayedBatchExporter(Component):
    """Export the Oxigesti Product prices.

    For every product in the list, a delayed job is created.
    """

    _name = "oxigesti.product.pricelist.item.delayed.batch.exporter"
    _inherit = "oxigesti.delayed.batch.exporter"

    # def run(self, domain=None):
    #     super().run_common(domain=domain)


class ProductPricelistItemDirectBatchExporter(Component):
    """Export the Oxigesti Product prices.

    For every product in the list, a direct job is created.
    """

    _name = "oxigesti.product.pricelist.item.direct.batch.exporter"
    _inherit = "oxigesti.direct.batch.exporter"

    # def run(self, domain=None):
    #     super().run_common(domain=domain)


class ProductPricelistItemExporter(Component):
    _name = "oxigesti.product.pricelist.item.exporter"
    _inherit = "oxigesti.exporter"

    _apply_on = "oxigesti.product.pricelist.item"

    def run(self, relation, *args, **kwargs):
        partners = (
            self.env["res.partner"]
            .search(
                [
                    ("company_id", "=?", self.backend_record.company_id.id),
                ]
            )
            .filtered(lambda x: x.property_product_pricelist == relation.pricelist_id)
        )
        if partners:
            bindings = self.env[relation.oxigesti_bind_ids._name]
            for p in partners:
                bindings |= self.binder.wrap_binding(
                    relation,
                    binding_extra_vals={
                        "odoo_partner_id": p.id,
                        "deprecated": relation.is_deprecated(p),
                        "odoo_fixed_price": relation.fixed_price,
                    },
                )
        else:
            bindings = relation.oxigesti_bind_ids.filtered(
                lambda x: x.deprecated
                and x.odoo_partner_id.property_product_pricelist
                != relation.pricelist_id
            )
        for binding in bindings:
            super().run(binding, *args, **kwargs)

    # def run(self, relation, *args, **kwargs):
    #     partners = (
    #         self.env["res.partner"]
    #         .search(
    #             [
    #                 ("company_id", "=?", self.backend_record.company_id.id),
    #             ]
    #         )
    #         .filtered(lambda x: x.property_product_pricelist == relation.pricelist_id)
    #     )
    #     for p in partners:
    #         computed_external_id = self.binder._get_external_id(
    #             relation, extra_vals={"odoo_partner_id": p.id}
    #         )
    #         binding = self.binder.to_internal(computed_external_id)
    #         if binding and binding.odoo_id != relation:
    #             # old_binding = self.binder._find_binding(
    #             #     relation, binding_extra_vals={"odoo_partner_id": p.id}
    #             # )
    #             # if old_binding:
    #             #     old_binding.unlink()
    #             binding.odoo_id = relation
    #         # computed_external_id_hash = idhash(computed_external_id)
    #         # binding = self.env["oxigesti.product.pricelist.item"].search(
    #         #     [
    #         #         ("backend_id", "=", self.backend_record.id),
    #         #         ("external_id_hash", "=", computed_external_id_hash),
    #         #         ("odoo_partner_id", "=", p.id),
    #         #         ("odoo_id", "!=", relation.id),
    #         #     ]
    #         # )
    #         # if binding:
    #         #     binding.odoo_id = relation
    #         binding = self.binder.wrap_binding(
    #             relation,
    #             binding_extra_vals={
    #                 "odoo_partner_id": p.id,
    #                 "deprecated": relation.is_deprecated(p),
    #                 "odoo_fixed_price": relation.fixed_price,
    #             },
    #         )
    #         super().run(binding, *args, **kwargs)
    #     if not partners:
    #         for binding in relation.oxigesti_bind_ids.filtered(
    #             lambda x: x.deprecated
    #         ):
    #             super().run(binding, *args, **kwargs)

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
