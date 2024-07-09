# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)


# TODO: delete this file
# class WooCommerceBinding(models.AbstractModel):
#     _inherit = "woocommerce.binding"
#
#     def _prepare_relation(self, relation, record):
#         relation = super()._prepare_relation(relation, record)
#         iso_lang = self.env["res.lang"]._get_iso_code_from_wpml_code(
#             record.woocommerce_lang
#         )
#         if iso_lang:
#             return relation.with_context(lang=iso_lang, resync_export=True)
#         return relation
