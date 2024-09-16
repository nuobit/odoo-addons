# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WordPressIrChecksumBinder(Component):
    _inherit = "wordpress.ir.checksum.binder"

    # @property
    # def external_alt_id(self):
    #     return super().external_alt_id + ["lang"]

    # TODO: This funtions are the same as product wpml mixin
    def get_binding_domain(self, record):
        domain = super().get_binding_domain(record)
        wp_wpml_code = self.env["res.lang"]._get_wpml_code_from_iso_code(
            record._context.get("lang")
        )
        if wp_wpml_code:
            domain += [
                (
                    "wordpress_lang",
                    "=",
                    wp_wpml_code,
                )
            ]
        return domain

    def _additional_external_binding_fields(self, external_data):
        # TODO: this additional fields probably should be
        #  included in binding as m2o to res lang on upper binder
        return {
            **super()._additional_external_binding_fields(external_data),
            "wordpress_lang": external_data.get("lang") or self.env.context.get("lang"),
        }

    def _get_external_record_alt(self, relation, id_values):
        res = super()._get_external_record_alt(relation, id_values)
        if res:
            relation_wp_lang = self.env["res.lang"]._get_wpml_code_from_iso_code(
                relation.env.context.get("lang")
            )
            if res.get("lang") != relation_wp_lang:
                if res.get("translations") and res["translations"].get(
                    relation_wp_lang
                ):
                    adapter = self.component(usage="backend.adapter")
                    res = adapter.read(res["translations"][relation_wp_lang])
                else:
                    return None
        return res
