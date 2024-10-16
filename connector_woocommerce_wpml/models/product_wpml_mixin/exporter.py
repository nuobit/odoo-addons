# # Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# # License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
#
# from odoo.addons.component.core import AbstractComponent
#
#
# class WooCommerceProductWPMLMixinExporter(AbstractComponent):
#     _name = "woocommerce.product.wpml.mixin.record.direct.exporter"
#     _inherit = "connector.extension.generic.record.direct.exporter"
#
#     def wpml_run(self, relation, always=True, internal_fields=None):
#         res = []
#         langs_to_export = self.backend_record.language_ids.mapped("code")
#         for lang in langs_to_export:
#             result = super().run(
#                 relation.with_context(lang=lang),
#                 always=always,
#                 internal_fields=internal_fields,
#             )
#             res.append(result)
#         return res
