# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class PayrollSageLabourAgreementWageTypeLine(models.Model):
    _inherit = "payroll.sage.labour.agreement.wage.type.line"

    sage_bind_ids = fields.One2many(
        comodel_name="sage.payroll.sage.labour.agreement.wage.type.line",
        inverse_name="odoo_id",
        string="Sage Bindings",
    )


class PayrollSageLabourAgreementWageTypeLineBinding(models.Model):
    _name = "sage.payroll.sage.labour.agreement.wage.type.line"
    _inherit = "sage.binding"
    _inherits = {"payroll.sage.labour.agreement.wage.type.line": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="payroll.sage.labour.agreement.wage.type.line",
        string="Labour agreement wage type",
        required=True,
        ondelete="cascade",
    )

    backend_id = fields.Many2one(
        related="sage_labour_agreement_id.backend_id",
        string="Backend",
        readonly=True,
        store=True,
        # override 'sage.binding', can't be INSERTed if True:
        required=False,
    )

    sage_labour_agreement_id = fields.Many2one(
        comodel_name="sage.payroll.sage.labour.agreement",
        string="Sage Labour agreeement",
        required=True,
        ondelete="cascade",
        index=True,
    )

    # composed id
    sage_codigo_empresa = fields.Integer(string="CodigoEmpresa", required=True)
    sage_codigo_convenio = fields.Integer(string="CodigoConvenio", required=True)
    sage_fecha_registro_cv = fields.Date(string="FechaRegistroCV", required=True)
    sage_codigo_concepto_nom = fields.Integer(string="CodigoConceptoNom", required=True)

    _sql_constraints = [
        (
            "uniq",
            "unique(sage_labour_agreement_id, sage_codigo_empresa, "
            "sage_codigo_convenio, sage_fecha_registro_cv, sage_codigo_concepto_nom)",
            "Wage type line with same ID on Sage already exists.",
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sage_labour_agreement_id = vals["sage_labour_agreement_id"]
            binding = self.env["sage.payroll.sage.labour.agreement"].browse(
                sage_labour_agreement_id
            )
            vals["labour_agreement_id"] = binding.odoo_id.id
        return super().create(vals_list)
        # FIXME triggers function field
        # The amounts (amount_total, ...) computed fields on 'sale.order' are
        # not triggered when magento.sale.order.line are created.
        # It might be a v8 regression, because they were triggered in
        # v7. Before getting a better correction, force the computation
        # by writing again on the line.
        # line = binding.odoo_id
        # line.write({'price_unit': line.price_unit})
