from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurifyPurge(models.Model):
    _name = 'purify.purge'
    _description = 'Purge'

    name = fields.Char(string='Log')

    def button_purge(self):


        self.env.cr.execute('select * from ir_model')

        #row = self.env.cr.fetchone()

        #self.env['ir.ui.menu'].with_context(active_test=False).search([('action', '!=', False)])

        """
                Search for models that cannot be instantiated.
        """
        '''
        res = []
        for menu in self.env['ir.ui.menu'].with_context(active_test=False) \
                .search([('action', '!=', False)]):
            if menu.action.type != 'ir.actions.act_window':
                continue
            if (menu.action.res_model and menu.action.res_model not in
                self.env) or \
                    (menu.action.src_model and menu.action.src_model not in
                        self.env):
                res.append((0, 0, {
                    'name': menu.complete_name,
                    'menu_id': menu.id,
                }))
        if not res:
            raise UserError(_('No dangling menu entries found'))
        return res
        '''
        # menus (ir.ui.menu) no referenciats pel model data (ir.model.data) (posiblement duplicats)
        res = []
        for menu in self.env['ir.ui.menu'].with_context(active_test=False) \
                .search([('action', '!=', False)]):
            if menu.action.type != 'ir.actions.act_window':
                continue

            if not self.env['ir.model.data'].with_context(active_test=False) \
                .search([('model', '=', 'ir.ui.menu'), ('res_id', '=', menu.id)]):
                res.append(menu)

        for menu in res:
            menu.action.unlink()
            menu.unlink()

        # act windows (ir.act.window) no refenicat pel ui menu No es correte aiox no sha de tocar
        '''
        res = []
        for act_window in self.env['ir.actions.act_window'].with_context(active_test=False) \
                .search([]):
            #if act_window.type != 'ir.actions.act_window':
            #    continue
            if not self.env['ir.ui.menu'].with_context(active_test=False)\
                    .search([('action', '!=', False)])\
                    .filtered(lambda x: x.action.type == 'ir.actions.act_window' and x.action.id == act_window.id):
                res.append(act_window)

        '''

        # model data qiue no te el que diu que ha de tenir
        #self.name += 'pepe\n'


