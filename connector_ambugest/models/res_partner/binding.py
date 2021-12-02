# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models

from odoo.addons.queue_job.job import job


class ResPartner(models.Model):
    _inherit = "res.partner"

    ambugest_bind_ids = fields.One2many(
        comodel_name="ambugest.res.partner",
        inverse_name="odoo_id",
        string="Ambugest Bindings",
    )


class ResPartnerBinding(models.Model):
    _name = "ambugest.res.partner"
    _inherit = "ambugest.binding"
    _inherits = {"res.partner": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", required=True, ondelete="cascade"
    )

    ## composed id
    ambugest_empresa = fields.Integer(string="Empresa on Ambugest", required=True)
    ambugest_codiup = fields.Integer(string="CodiUP on Ambugest", required=True)

    _sql_constraints = [
        (
            "ambugest_res_partner",
            "unique(ambugest_empresa, ambugest_codiup)",
            "Partner with same ID on Ambugest already exists.",
        ),
    ]

    @job(default_channel="root.ambugest")
    def import_customers_since(self, backend_record=None, since_date=None):
        """ Prepare the import of partners modified on Ambugest """
        filters = {
            "EMPRESA": backend_record.ambugest_company_id,
        }
        now_fmt = fields.Datetime.now()
        self.env["ambugest.res.partner"].import_batch(
            backend=backend_record, filters=filters
        )
        backend_record.import_customers_since_date = now_fmt

        return True
