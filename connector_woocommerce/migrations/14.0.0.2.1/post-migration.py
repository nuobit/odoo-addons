# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

from odoo import fields

from odoo.addons.connector_woocommerce.common.tools import is_blank_html

_logger = logging.getLogger(__name__)


def _exported_blank_description(template):
    """Whether the old export sent placeholder markup for this template."""
    if template.public_description:
        description = template.public_description
    else:
        description = (
            template.product_variant_id.variant_public_description
            if len(template.product_variant_ids) == 1
            else None
        )
    # An already empty value has no placeholder to clear on the website.
    return bool(description) and is_blank_html(description)


@openupgrade.migrate()
def migrate(env, version):
    now = fields.Datetime.now()
    backends = env["woocommerce.backend"].with_context(active_test=False).search([])
    for backend in backends:
        templates = (
            env["woocommerce.product.template"]
            .with_context(active_test=False)
            .search([("backend_id", "=", backend.id)])
            .odoo_id
        )
        variants = (
            env["woocommerce.product.product"]
            .with_context(active_test=False)
            .search([("backend_id", "=", backend.id)])
            .odoo_id
        )
        for language in backend.lang_ids:
            blank_templates = templates.with_context(lang=language.code).filtered(
                _exported_blank_description
            )
            blank_variants = variants.with_context(lang=language.code).filtered(
                lambda product: bool(product.variant_public_description)
                and is_blank_html(product.variant_public_description)
            )
            # The normal batches split simple templates from variable products.
            # A variable parent's description travels through its variant jobs;
            # a simple product's single-variant fallback travels with its template.
            templates_to_export = blank_templates | blank_variants.product_tmpl_id
            variants_to_export = blank_variants | blank_templates.product_variant_ids
            for products in (templates_to_export, variants_to_export):
                products.woocommerce_write_date = now
                _logger.info(
                    "Blank HTML re-export: backend %s, language %s, %s: %s records",
                    backend.id,
                    language.code,
                    products._name,
                    len(products),
                )
                _logger.debug(
                    "Blank HTML re-export: backend %s, language %s, %s IDs: %s",
                    backend.id,
                    language.code,
                    products._name,
                    products.ids,
                )
