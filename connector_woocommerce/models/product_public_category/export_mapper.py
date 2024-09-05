# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping


class WooCommerceProductPublicCategoryExportMapper(Component):
    _name = "woocommerce.product.public.category.export.mapper"
    _inherit = "woocommerce.export.mapper"

    _apply_on = "woocommerce.product.public.category"

    @mapping
    def parent_id(self, record):
        binder = self.binder_for("woocommerce.product.public.category")
        if record.parent_id:
            values = binder.get_external_dict_ids(record.parent_id)
            return {"parent": values["id"]}

    @changed_by("name")
    @mapping
    def name(self, record):
        if "  " in record.name:
            raise ValidationError(
                _(
                    "The category '%s' has a double space in the name. "
                    "WooCommerce only allow one space. Please, remove it before export."
                )
                % record.name
            )
        return {
            "name": record.with_context(lang=self.backend_record.language_id.code).name
        }

    @mapping
    def description(self, record):
        return {
            "description": record.with_context(
                lang=self.backend_record.language_id.code
            ).description
            or ""
        }

    def _get_slug_name(self, record):
        return record.with_context(lang=self.backend_record.language_id.code).slug_name

    @mapping
    def slug(self, record):
        slug = self._get_slug_name(record)
        if slug:
            return {"slug": slug}
