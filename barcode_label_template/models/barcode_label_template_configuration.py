# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class BarcodeLabelTemplateConfiguration(models.Model):
    _name = "barcode.label.template.configuration"
    _description = "Barcode Label Template Configuration"
    _order = "default desc"

    @property
    def BARCODE_TYPE_SELECTION(self):
        return [
            ("gs1-datamatrix", "GS1-Datamatrix"),
            ("EAN13", "EAN13"),
        ]

    name = fields.Char(required=True)
    template = fields.Binary()
    template_name = fields.Char()
    paperformat_id = fields.Many2one(comodel_name="report.paperformat", required=True)
    default = fields.Boolean()
    barcode_type = fields.Selection(
        selection=lambda self: self.BARCODE_TYPE_SELECTION,
        required=True,
        default="gs1-datamatrix",
    )
    check_barcode_encoding = fields.Boolean(
        compute="_compute_check_barcode_encoding",
        store=True,
        readonly=False,
        help="Check if the barcode encoding is correct",
    )
    humanreadable = fields.Boolean(
        default=True,
        help="Show the human readable text",
        string="Human readable",
    )

    resolution_ppi = fields.Integer(
        default=600,
        string="Resolution (ppi)",
        required=True,
    )

    correction_ratio_pxmm = fields.Float(
        digits=(5, 4),
        string="Correction ratio px/mm",
        required=True,
        default=0.85,
    )

    @api.depends("barcode_type")
    def _compute_check_barcode_encoding(self):
        for rec in self:
            if rec.barcode_type == "EAN13":
                rec.check_barcode_encoding = True

    position_x = fields.Float()
    position_y = fields.Float()

    def _compute_dimension_value(self, dimension, ratio=1):
        self.ensure_one()
        if dimension == "width":
            self.width = int(self.height / ratio)
        elif dimension == "height":
            self.height = int(self.width * ratio)
        else:
            raise ValidationError(_("Invalid dimension: '%s'") % dimension)

    def _compute_dimension(self, dimension):
        for rec in self:
            if rec.barcode_type == "EAN13":
                if rec.check_barcode_encoding:
                    rec._compute_dimension_value(dimension, ratio=1 / 2)
            elif rec.barcode_type == "gs1-datamatrix":
                rec._compute_dimension_value(dimension, ratio=1 / 1)

    width = fields.Float(
        compute="_compute_width",
        store=True,
        readonly=False,
    )

    @api.depends("height")
    def _compute_width(self):
        self._compute_dimension("width")

    height = fields.Float(
        compute="_compute_height",
        store=True,
        readonly=False,
    )

    @api.depends("width", "check_barcode_encoding", "barcode_type")
    def _compute_height(self):
        self._compute_dimension("height")

    configuration_field_ids = fields.One2many(
        comodel_name="barcode.label.template.configuration.field",
        inverse_name="configuration_id",
        string="Field configuration",
    )

    @api.constrains("default")
    def _check_default(self):
        for rec in self:
            if rec.default:
                config = self.search([("id", "!=", rec.id), ("default", "=", True)])
                if config:
                    raise ValidationError(_("There is already a default configuration"))
