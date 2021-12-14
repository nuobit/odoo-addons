# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models

from odoo.addons.queue_job.job import job


class ResPartner(models.Model):
    _inherit = "res.partner"

    sage_bind_ids = fields.One2many(
        comodel_name="sage.res.partner",
        inverse_name="odoo_id",
        string="Sage Bindings",
    )


class ResPartnerBinding(models.Model):
    _name = "sage.res.partner"
    _inherit = "sage.binding"
    _inherits = {"res.partner": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", required=True, ondelete="cascade"
    )

    ## composed id
    sage_codigo_empresa = fields.Integer(string="CodigoEmpresa", required=True)
    sage_codigo_empleado = fields.Integer(string="CodigoEmpleado", required=True)

    _sql_constraints = [
        (
            "sage_res_partner",
            "unique(sage_codigo_empresa, sage_codigo_empleado)",
            "Partner with same ID on Sage already exists.",
        ),
    ]

    @job(default_channel="root.sage")
    def import_contacts_since(self, backend_record=None, since_date=None):
        """ Prepare the import of partners modified on Sage """
        filters = {
            "CodigoEmpresa": backend_record.sage_company_id,
        }
        now_fmt = fields.Datetime.now()
        self.env["sage.res.partner"].import_batch(
            backend=backend_record, filters=filters
        )
        backend_record.import_partners_since_date = now_fmt

        return True
