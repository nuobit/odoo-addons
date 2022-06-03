# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class ProductTemplateBinder(Component):
    _name = "veloconnect.product.template.binder"
    _inherit = "veloconnect.binder"

    _apply_on = "veloconnect.product.template"

    _external_field = "SellersItemIdentificationID"
    _internal_field = "veloconnect_seller_item_id"
    _internal_alt_field = ["barcode", "seller_ids"]

    def _get_internal_record_domain(self, values):
        query = """ SELECT t.id
                    FROM product_template t
                    WHERE (t.company_id IS NULL OR t.company_id = %(company_id)s) AND (
                        (
                            EXISTS (
                                    SELECT 1
                                    FROM product_product i
                                    WHERE i.product_tmpl_id = t.id AND
                                          i.barcode = %(barcode)s
                            ) AND (
                                EXISTS (
                                    SELECT 1
                                    FROM product_supplierinfo i
                                    WHERE i.product_tmpl_id = t.id AND
                                          i.name = %(name)s AND
                                          i.product_code = %(product_code)s
                                ) OR
                                NOT EXISTS (
                                    SELECT 1
                                    FROM product_supplierinfo i
                                    WHERE i.product_tmpl_id = t.id AND
                                          i.name = %(name)s
                                ) OR
                                NOT EXISTS (
                                    SELECT 1
                                    FROM product_supplierinfo i
                                    WHERE i.product_tmpl_id = t.id AND
                                          i.name = %(name)s AND
                                          i.product_code IS NOT NULL
                                )
                            )
                        ) OR (
                            EXISTS (
                                    SELECT 1
                                    FROM product_product i
                                    WHERE i.product_tmpl_id = t.id AND
                                          ( i.barcode IS NULL OR i.barcode = %(barcode)s)
                            ) AND (
                                EXISTS (
                                    SELECT 1
                                    FROM product_supplierinfo i
                                    WHERE i.product_tmpl_id = t.id AND
                                          i.name = %(name)s AND
                                          i.product_code = %(product_code)s
                                )
                            )
                        )
                    )
                    """

        self.env.cr.execute(
            query,
            {
                "company_id": self.backend_record.company_id.id,
                "barcode": values["barcode"],
                "name": self.backend_record.partner_id.id,
                "product_code": values["seller_ids"][0][2]["product_code"],
            },
        )
        return [("id", "in", [x[0] for x in self.env.cr.fetchall()])]

    def _get_internal_record_alt(self, model_name, values):
        template = super()._get_internal_record_alt(model_name, values)
        if len(template) == 1 and len(template.product_variant_ids) > 1:
            raise ValidationError(
                _(
                    "Not supported: Product template %s with id %s has more than one variant."
                )
                % (template.name, template.id)
            )
        return template
