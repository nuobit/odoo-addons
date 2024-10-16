# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class IrChecksum(models.Model):
    _name = "ir.checksum"

    checksum = fields.Char(
        string="Checksum/SHA1",
        size=40,
        index=True,
        readonly=True,
    )
    store_fname = fields.Char(
        string="Stored Filename",
        compute="_compute_store_fname_mimetype",
    )
    mimetype = fields.Char(
        string="Mime Type",
        compute="_compute_store_fname_mimetype",
    )

    def _compute_store_fname_mimetype(self):
        for rec in self:
            store_fname, mimetype = False, False
            # TODO: Use this search instead of query
            # self.env["ir.attachment"].search(
            #     [
            #         ("checksum", "=", rec.checksum),
            #         ("res_id", "!=", False)
            #     ],
            #     limit=1,
            # )
            # We cant use search() in ir.attachment
            self.env.cr.execute(
                "SELECT * FROM ir_attachment WHERE checksum = %s LIMIT 1",
                (rec.checksum,),
            )
            attachment = self.env.cr.dictfetchall()
            if attachment:
                store_fname = attachment[0]["store_fname"]
                mimetype = attachment[0]["mimetype"]
            rec.store_fname = store_fname
            rec.mimetype = mimetype

    title = fields.Char(
        translate=True,
    )
    alternate_text = fields.Text(
        translate=True,
    )

    _sql_constraints = [
        (
            "external_uniq",
            "unique(checksum)",
            "A checksum already exists with the same External (checksum) ID.",
        ),
    ]

    def write(self, vals):
        if "checksum" in vals:
            raise ValidationError(
                _("You cannot change the checksum of an existing record.")
            )
        return super().write(vals)
