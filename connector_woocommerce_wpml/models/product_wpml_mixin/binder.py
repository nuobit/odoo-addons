# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class WooCommerceProductWPMLMixinBinder(AbstractComponent):
    _name = "woocommerce.product.wpml.mixin.binder"
    _inherit = "connector.extension.binder"

    def wpml_get_binding_domain(self, record):
        domain = super().get_binding_domain(record)
        wp_wpml_code = self.env["res.lang"]._get_wpml_code_from_iso_code(
            record._context.get("lang")
        )
        if wp_wpml_code:
            domain += [
                (
                    "woocommerce_lang",
                    "=",
                    wp_wpml_code,
                )
            ]
        return domain

    def wpml_additional_external_binding_fields(self, external_data, relation):
        # TODO: this additional fields probably should be
        #  included in binding as m2o to res lang on upper binder
        return {
            **super()._additional_external_binding_fields(external_data, relation),
            "woocommerce_lang": external_data["lang"],
        }

    def wpml_get_master_binding(self, relation):
        return self.model.with_context(active_test=False).search(
            [
                (self._odoo_field, "=", relation.id),
                (self._backend_field, "=", self.backend_record.id),
                ("woocommerce_master_lang", "=", True),
            ],
            limit=1,
        )

    def _wpml_read_translation(self, relation, record, translation_id):
        adapter = self.component(usage="adapter")
        return adapter.read(translation_id)

    def _wpml_redirect_record_lang(self, relation, record):
        relation_wp_lang = self.env["res.lang"]._get_wpml_code_from_iso_code(
            relation.env.context.get("lang")
        )
        if record.get("lang") != relation_wp_lang:
            if record.get("translations") and record["translations"].get(
                relation_wp_lang
            ):
                return self._wpml_read_translation(
                    relation, record, record["translations"][relation_wp_lang]
                )
            return None
        return record

    def _get_external_record_alt_fallback(self, relation, id_values):
        record = super()._get_external_record_alt_fallback(relation, id_values)
        if not record:
            # Non-master languages don't export the SKU, so their alternate
            # key is always incomplete: reach the external record through the
            # master language binding instead.
            master_binding = self.wpml_get_master_binding(relation)
            if master_binding:
                adapter = self.component(usage="adapter")
                record = adapter.read(self.dict2id(master_binding, in_field=True))
        return record or {}
