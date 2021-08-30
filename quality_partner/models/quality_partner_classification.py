# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

MAP_LEVELS = {
    "type": (0, _("Type")),
    "criticality": (1, _("Criticality")),
    "description": (2, _("Description")),
}
MAP_LEVELS_ORD = {v[0]: (k, v[1]) for k, v in MAP_LEVELS.items()}
LEVELS = [
    (k, trl) for k, (_ord, trl) in sorted(MAP_LEVELS.items(), key=lambda x: x[1][0])
]


class QualityPartnerClassification(models.Model):
    _name = "quality.partner.classification"
    _inherit = "quality.tree.mixin"
    _description = "Quality Partner Classification"
    _rec_name = "complete_name"
    _order = "sequence"

    name = fields.Char(string="Name", translate=True, required=True)
    code = fields.Char(string="Code")

    level_type = fields.Selection(selection=LEVELS, string="Level type", required=True)

    description = fields.Text(string="Description")

    parent_id = fields.Many2one(
        comodel_name="quality.partner.classification",
        string="Parent",
        ondelete="restrict",
    )

    document_type_ids = fields.Many2many(
        comodel_name="quality.partner.document.type",
        relation="quality_partner_classification_document_type_rel",
        column1="classification_id",
        column2="document_type_id",
        string="Document types",
    )

    sequence = fields.Integer(string="Sequence")

    mandatory_document_type_ids = fields.Many2many(
        comodel_name="quality.partner.document.type",
        compute="_compute_mandatory_document_type_ids",
        string="Mandatory document types",
    )

    def _get_document_type_ids(self):
        self.ensure_one()
        if self.level_type == "criticality":
            return self.document_type_ids
        else:
            if not self.parent_id:
                return self.env["quality.partner.document.type"]
            else:
                return self.parent_id._get_document_type_ids()

    @api.depends("document_type_ids", "parent_id")
    def _compute_mandatory_document_type_ids(self):
        for rec in self:
            rec.mandatory_document_type_ids = rec._get_document_type_ids()

    @api.onchange("level_type", "parent_id")
    def _onchange_level_type_parent(self):
        if not self.parent_id:
            self.level_type = MAP_LEVELS_ORD[0][0]
        else:
            parent_level_type_ord_next = MAP_LEVELS[self.parent_id.level_type][0] + 1
            if parent_level_type_ord_next not in MAP_LEVELS_ORD:
                self.level_type = False
            else:
                self.level_type = MAP_LEVELS_ORD[parent_level_type_ord_next][0]

    @api.onchange("level_type", "document_type_ids")
    def _onchange_level_type_document_type(self):
        if self.level_type != "criticality" and self.document_type_ids:
            self.document_type_ids = False

    @api.constrains("parent_id")
    def _check_parent_id(self):
        objs = (
            self.env[self._name]
            .search([])
            .sorted(lambda x: (x._get_root().id, x.level, x.name))
        )

        for seq, rec in list(enumerate(objs)):
            rec.sequence = seq

    @api.constrains("level_type", "document_type_ids")
    def _check_document_per_level_type(self):
        for rec in self:
            if rec.level_type != "criticality":
                if rec.document_type_ids:
                    rec.document_type_ids = False
            else:
                if not rec.document_type_ids:
                    raise ValidationError(
                        _(
                            "You must provide a document types for the level type selected"
                        )
                    )

    @api.constrains("level_type", "parent_id", "parent_id.level_type")
    def _check_level_type_parent(self):
        for rec in self:
            if rec.parent_id == rec:
                raise ValidationError(
                    _("The parent cannot be the same as current record")
                )
            if not (
                (not rec.parent_id and rec.level_type == MAP_LEVELS_ORD[0][0])
                or (
                    rec.parent_id
                    and MAP_LEVELS[rec.level_type][0]
                    == MAP_LEVELS[rec.parent_id.level_type][0] + 1
                )
            ):
                raise ValidationError(
                    _(
                        "Wrong inheritance, the level type selected it's not "
                        "compatible with the selected parent"
                    )
                )
