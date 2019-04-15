# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError


class LightingExportTemplate(models.Model):
    _name = 'lighting.export.template'
    _order = 'name'

    name = fields.Char(required=True)

    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as avatar for this template, limited to 1024x1024px", )
    image_medium = fields.Binary("Medium-sized image", attachment=True,
                                 help="Medium-sized image of this contact. It is automatically " \
                                      "resized as a 128x128px image, with aspect ratio preserved. " \
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image", attachment=True,
                                help="Small-sized image of this contact. It is automatically " \
                                     "resized as a 64x64px image, with aspect ratio preserved. " \
                                     "Use this field anywhere a small image is required.")

    field_ids = fields.One2many(comodel_name='lighting.export.template.field', inverse_name='template_id',
                                string='Fields', copy=True)

    attachment_ids = fields.One2many(comodel_name='lighting.export.template.attachment', inverse_name='template_id',
                                     string='Attachments', copy=True)

    lang_ids = fields.Many2many(comodel_name='res.lang',
                                relation='lighting_export_template_lang_rel',
                                column1='template_id', column2='lang_id',
                                string='Languages',
                                domain=[('active', '=', True)],
                                track_visibility='onchange')

    hide_empty_fields = fields.Boolean(string="Hide empty fields", default=True)

    output_type = fields.Selection(selection=[], string="Output type", required=True)

    domain = fields.Text(string='Domain')

    _sql_constraints = [('name_uniq', 'unique (name)', 'The template name must be unique!'),
                        ]

    @api.multi
    def add_all_fields(self):
        for rec in self:
            lighting_product_fields_ids = self.env['ir.model.fields'].search([
                ('model', '=', 'lighting.product'),
                ('name', 'in', list(self.env['lighting.product'].fields_get().keys())),
            ])
            new_field_ids = lighting_product_fields_ids \
                .filtered(lambda x: x.id not in rec.field_ids.mapped('field_id.id')) \
                .sorted(lambda x: x.id)

            max_sequence = max(rec.field_ids.mapped('sequence') or [0])
            rec.field_ids = [(0, False, {'sequence': max_sequence + i,
                                         'field_id': x.id,
                                         'translate': x.translate,
                                         }) for i, x in enumerate(new_field_ids, 1)]

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        result = super().write(vals)

        return result

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {},
                       name=_('%s (copy)') % self.name,
                       image=False,
                       image_medium=False,
                       image_small=False,
                       )

        return super().copy(default)


class LightingExportTemplateField(models.Model):
    _name = 'lighting.export.template.field'
    _order = 'sequence'

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")

    sequence_aux = fields.Integer(related='sequence', string="Sequence")

    field_id = fields.Many2one(comodel_name='ir.model.fields', ondelete='cascade',
                               domain=[('model', '=', 'lighting.product')],
                               string='Field', required=True)
    field_name = fields.Char(related='field_id.name', readonly=True)
    field_ttype = fields.Selection(related='field_id.ttype', readonly=True)

    subfield_name = fields.Char(string='Subfield')

    translate = fields.Boolean(string='Translate')

    label = fields.Char(string='Label', translate=True)

    template_id = fields.Many2one(comodel_name='lighting.export.template', ondelete='cascade',
                                  string='Template', required=True)

    _sql_constraints = [
        ('line_uniq', 'unique (field_id,template_id)', 'The template field must be unique per template!'),
    ]


class LightingExportTemplateAttachment(models.Model):
    _name = 'lighting.export.template.attachment'
    _order = 'sequence'

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")

    type_id = fields.Many2one(comodel_name='lighting.attachment.type', ondelete='cascade',
                              string='Type', required=True)
    resolution = fields.Char(string='Resolution')

    template_id = fields.Many2one(comodel_name='lighting.export.template', ondelete='cascade',
                                  string='Template', required=True)

    _sql_constraints = [
        ('line_uniq', 'unique (type_id,template_id)', 'The template attachment must be unique per template!'),
    ]
