# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)


#
# class WooCommerceProductPublicCategoryExportMapper(Component):
#     _inherit = "woocommerce.product.public.category.export.mapper"
#
#     @changed_by("name")
#     @mapping
#     def name(self, record):
#         dict_name = super().name(record)
#         if "name" in dict_name:
#             if dict_name["name"] != record.name:
#                 dict_name["name"] = record.name
#         return dict_name
#
#     # TODO: REMOVE THIS COMMENT: we need lang on write because woocommerce
#     #  can't be write name with id as a external_id, we need name+lang.
#     # TODO: REMOVE THIS LANG FROM MAPPER!!
#     # @only_create
#     @mapping
#     def lang(self, record):
#         lang_code = record._context.get("lang")
#         return {"lang": lang_code[:2]}
#
#     @only_create
#     @mapping
#     def translation_of(self, record):
#         iso_code = record._context.get("lang")
#         if iso_code:
#             other_binding_backend = record.woocommerce_bind_ids.filtered(
#                 lambda x: x.backend_id == self.backend_record
#                 and x.woocommerce_lang != iso_code[:2]
#             )
#             translation_of = None
#             # TODO: REVIEW: can we send two values as a list?
#             for obb in other_binding_backend:
#                 translation_of = obb.woocommerce_idpubliccategory
#             return {"translation_of": translation_of}
