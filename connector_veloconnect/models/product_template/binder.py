# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.odoo.exceptions import ValidationError


def _(param):
    pass


class ProductTemplateBinder(Component):
    _name = 'veloconnect.product.template.binder'
    _inherit = 'veloconnect.binder'

    _apply_on = 'veloconnect.product.template'

    _external_field = 'StandardItemIdentification'
    _internal_field = 'veloconnect_ean'
    _internal_alt_field = "barcode"

    def _get_internal_record_alt(self, model_name, values):
        template = super()._get_internal_record_alt(model_name, values)
        if len(template) == 1 and len(template.product_variant_ids) > 1:
            raise ValidationError(_("Not supported: Product template %s has more than one variant.") % template.name)
        return template
