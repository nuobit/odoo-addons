# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @api.returns('self')
    def get_user_roots(self):
        """ Return all root menu ids visible for the user.

        :return: the root menu ids
        :rtype: list(int)
        """
        if not self.env.user.has_group('lighting_topbar.topbar_group_hide'):
            return super(IrUiMenu, self).get_user_roots()

        domain = []
        if self.env['ir.module.module'].sudo().search([('name', '=', 'lighting'),
                                                ('state', '=', 'installed')]):
            domain.append(self.env.ref('lighting.lighting_menu').id)

        if self.env['ir.module.module'].sudo().search([('name', '=', 'lighting_portal'),
                                                ('state', '=', 'installed')]):
            domain.append(self.env.ref('lighting_portal.portal_menu_root').id)

        return self.search([('parent_id', '=', False), ('id', 'in', domain)])