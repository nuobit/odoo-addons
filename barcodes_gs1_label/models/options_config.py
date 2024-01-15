# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class BarcodesGS1LabelOptionsConfig(models.Model):
    _name = "barcodes.gs1.label.options.config"
    _description = "Barcodes GS1 Label Options Config"

    name = fields.Char(required=True)

    default = fields.Boolean()

    @api.model
    def _default_company_id(self):
        return self.env.company

    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda self: self._default_company_id(),
        readonly=True,
    )

    @property
    def BARCODE_TYPE_SELECTION(self):
        return [
            ("gs1-128", "GS1-128"),
            ("gs1-datamatrix", "GS1-Datamatrix"),
            ("ean13-code128", "EAN13 + Code128"),
            ("ean13", "EAN13"),
        ]

    barcode_type = fields.Selection(
        string="Barcode type",
        selection=lambda self: self.BARCODE_TYPE_SELECTION,
        required=True,
    )

    @api.constrains("default")
    def _check_default(self):
        for rec in self:
            if rec.default:
                if (
                    self.search_count(
                        [("default", "=", True), ("company_id", "=", rec.company_id.id)]
                    )
                    > 1
                ):
                    raise UserError(
                        _("Only one label configuration can be set as default")
                    )

    format_id = fields.Many2one(
        string="Label format",
        comodel_name="barcodes.gs1.label.options.format",
        required=True,
    )

    show_price = fields.Boolean(string="Show price")
    show_price_currency = fields.Boolean(string="Show currency")

    def name_get(self):
        res = []
        for rec in self:
            name = "%s - %s (%g x %g mm) [%s] - %s" % (
                rec.name,
                rec.format_id.paperformat_id.name,
                rec.format_id.label_width,
                rec.format_id.label_height,
                rec.format_id.page_max_labels,
                rec.barcode_type,
            )
            res.append((rec.id, name))
        return res
