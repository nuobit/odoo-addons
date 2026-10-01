# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.connector_woocommerce.tests.common import WooCommerceCase


class WooCommerceWPMLCase(WooCommerceCase):
    """The base fixtures with a second export language and WPML bindings."""

    @classmethod
    def _setup_languages(cls):
        english = cls.env.ref("base.lang_en")
        spanish = cls.env["res.lang"]._activate_lang("es_ES")
        english.wordpress_wpml_lang_code = "en"
        spanish.wordpress_wpml_lang_code = "es"
        return english + spanish

    @classmethod
    def _template_binding_values(cls, template, woocommerce_idproduct):
        return {
            **super()._template_binding_values(template, woocommerce_idproduct),
            "woocommerce_lang": "en",
            "woocommerce_master_lang": True,
        }

    @classmethod
    def _variant_binding_values(cls, variant, woocommerce_idproduct):
        return {
            **super()._variant_binding_values(variant, woocommerce_idproduct),
            "woocommerce_lang": "en",
            "woocommerce_master_lang": True,
        }
