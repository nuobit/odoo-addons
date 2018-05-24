# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    def _get_siblings(self):
        if self.parent_id:
            childs = self.parent_id.child_id
        else:
            childs = self.env['product.public.category'].search([('parent_id', '=', False)])

        return childs.sorted(lambda x: (x.sequence, x.name))

    def _get_ancestors(self):
        parent_active_ancestors = []
        if self.parent_id:
            parent_active_ancestors = self.parent_id._get_ancestors()

        active_level = []
        for e in self._get_siblings():
            e9 = {}
            if e.id == self.id:
                e9['active'] = 'True'
            active_level.append({e:e9})

        return parent_active_ancestors + [active_level]

    def get_menu_structure(self):
        active_ancestors = self._get_ancestors()

        active_level = []
        for e in self.child_id:
            active_level.append({e: {}})

        active_ancestors.append(active_level)
        
        return active_ancestors
