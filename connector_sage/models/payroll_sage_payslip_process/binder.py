# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class PayrollSagePayslipProcessBinder(Component):
    """Bind records and give odoo/sage ids correspondence

    Binding models are models called ``sage.{normal_model}``,
    like ``sage.res.partner`` or ``sage.product.product``.
    They are ``_inherits`` of the normal models and contains
    the Sage ID, the ID of the Sage Backend and the additional
    fields belonging to the Sage instance.
    """

    _name = "sage.payroll.sage.payslip.process.binder"
    _inherit = "sage.binder"

    _apply_on = "sage.payroll.sage.payslip.process"

    _external_field = [
        "sage_codigo_empresa",
        "sage_tipo_proceso",
    ]
