# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class ResPartnerBinder(Component):
    """Bind records and give odoo/sage ids correspondence

    Binding models are models called ``sage.{normal_model}``,
    like ``sage.res.partner`` or ``sage.product.product``.
    They are ``_inherits`` of the normal models and contains
    the Sage ID, the ID of the Sage Backend and the additional
    fields belonging to the Sage instance.
    """

    _name = "sage.res.partner.binder"
    _inherit = "sage.binder"

    _apply_on = "sage.res.partner"

    _external_field = ["sage_codigo_empresa", "sage_codigo_empleado"]

    def to_binding_from_external_key(self, internal_data):
        odoo_id_field = self.binder_for()._odoo_field
        values = internal_data.values(for_create=True)
        if "vat" not in values:
            raise ValidationError(_("The 'VAT' field is not found in mapper."))
        if values["vat"]:
            relation_model_name = self.model[odoo_id_field]._name
            relation = (
                self.env[relation_model_name]
                .with_company(self.backend_record.company_id)
                .search([("vat", "=", values["vat"])])
            )
            if len(relation) > 1:
                raise ValidationError(
                    _("More than one partner with the same vat (%s) found")
                    % values["vat"]
                )
            if relation:
                return self.model.create(
                    {
                        **internal_data.values(),
                        odoo_id_field: relation.id,
                    }
                )
        return self.model
