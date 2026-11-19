# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
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
            partners = (
                self.env[relation_model_name]
                .with_company(self.backend_record.company_id)
                .search([("vat", "=", values["vat"])])
            )
            # Odoo copies the VAT of a commercial partner to its contacts:
            # only the partner that owns the VAT counts
            owners = partners.filtered(
                lambda partner: partner.commercial_partner_id == partner
            )
            if len(owners) > 1:
                raise ValidationError(
                    _(
                        "More than one partner owns this Tax ID "
                        "(partner IDs: %(ids)s). "
                        "Merge them, or correct the wrong Tax ID, and retry."
                    )
                    % {"ids": ", ".join(str(owner_id) for owner_id in owners.ids)}
                )
            elif owners:
                return self.model.create(
                    {
                        **internal_data.values(),
                        odoo_id_field: owners.id,
                    }
                )
            else:
                return self.model
        return self.model
