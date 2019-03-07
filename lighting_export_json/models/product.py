# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api


class LightingProduct(models.Model):
    _inherit = 'lighting.product'

    recess_dimension_display = fields.Char(compute='_compute_recess_dimension_display', string='Cut hole dimensions')

    @api.depends('recess_dimension_ids',
                 'recess_dimension_ids.type_id',
                 'recess_dimension_ids.value',
                 'recess_dimension_ids.sequence')
    def _compute_recess_dimension_display(self):
        for prod in self:
            same_uom = True
            uoms = set()
            dims = prod.recess_dimension_ids
            for rec in dims:
                if rec.type_id.uom not in uoms:
                    if not uoms:
                        uoms.add(rec.type_id.uom)
                    else:
                        same_uom = False
                        break

            res_label = ' x '.join(['%s' % x.type_id.name for x in dims])
            res_value = ' x '.join(['%g' % x.value for x in dims])

            if same_uom:
                res_label = '%s (%s)' % (res_label, uoms.pop())
            else:
                res_value = ' x '.join(['%g%s' % (x.value, x.type_id.uom) for x in dims])

            prod.recess_dimension_display = '%s: %s' % (res_label, res_value)

    search_material_ids = fields.Many2many(comodel_name='lighting.product.material',
                                           compute='_compute_search_material')

    @api.depends('body_material_ids',
                 'diffusor_material_ids',
                 'frame_material_ids',
                 'reflector_material_ids')
    def _compute_search_material(self):
        fields = [
            'body_material_ids', 'diffusor_material_ids',
            'frame_material_ids', 'reflector_material_ids',
            # 'blade_material_ids',
        ]
        for rec in self:
            materials_s = set()
            for field in fields:
                objs = getattr(rec, field)
                if objs:
                    materials_s |= set([x.id for x in objs])

            if materials_s:
                objs = self.env['lighting.product.material'].browse(list(materials_s))
                rec.search_material_ids = [(4, x.id, False) for x in objs.sorted(lambda x: x.display_name)]

    # search_dimension_ids = fields.One2many(comodel_name='lighting.product.dimension',
    #                                       inverse_name='product_id', compute='pepe')
    #
    # def pepe(self):
    #     for rec in self:
    #         rec.search_dimension_ids = [(0, False, {'product_id':rec.id, 'value': 78, 'sequence': 3, 'type_id': 9, 'name': 'oo'})]
