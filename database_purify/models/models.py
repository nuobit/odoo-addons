from openerp import api, fields, models, _
from openerp.exceptions import UserError
from psycopg2 import ProgrammingError
from openerp.tests.common import TransactionCase

class PurifyPurge(models.Model, TransactionCase):
    _name = 'purify.purge'
    _description = 'Purge'

    name = fields.Char(string='Log')

    @api.multi
    def button_purge(self):
        ###### Orphaned column
        # create an orphaned column
        '''
        self._cr.execute(
            'alter table res_users add column database_cleanup_test1 int')
        self._cr.execute(
            'alter table res_users add column database_cleanup_test2 int')
        '''
        #purge_columns = self.env['cleanup.purge.wizard.column'].create({})
        #purge_columns.purge_all()
        # must be removed by the wizard
        #with self.assertRaises(ProgrammingError):
        #    with self.env.cursor() as cr:
        #        cr.execute('select database_cleanup_test from res_users')

        ######### Orphaned data
        # create a data entry pointing nowhere
        '''
        self._cr.execute('select max(id) + 1 from res_users')
        self.env['ir.model.data'].create({
            'module': 'database_cleanup',
            'name': 'test_no_data_entry1',
            'model': 'res.users',
            'res_id': self._cr.fetchone()[0],
        })
        self._cr.execute('select max(id) + 1 from res_users')
        self.env['ir.model.data'].create({
            'module': 'database_cleanup',
            'name': 'test_no_data_entry2',
            'model': 'res.users',
            'res_id': self._cr.fetchone()[0],
        })
        '''
        #purge_data = self.env['cleanup.purge.wizard.data'].create({})
        #purge_data.purge_all()
        # must be removed by the wizard
        #with self.assertRaises(ValueError):
        #    self.env.ref('database_cleanup.test_no_data_entry')

        ######### Orphaned Models
        # create a nonexistent model
        self.env['ir.model'].create({
            'name': 'Database cleanup test model1',
            'model': 'x_database.cleanup.test.model1',
        })
        self.env['ir.model'].create({
            'name': 'Database cleanup test model2',
            'model': 'x_database.cleanup.test.model2',
        })
        self._cr.execute(
            'insert into ir_attachment (name, res_model, res_id, type) values '
            "('test attachment', 'database.cleanup.test.model1', 42, 'binary')")
        self._cr.execute(
            'insert into ir_attachment (name, res_model, res_id, type) values '
            "('test attachment', 'database.cleanup.test.model2', 42, 'binary')")


        self.env.models.pop('x_database.cleanup.test.model1')
        self.env._pure_function_fields.pop('x_database.cleanup.test.model1')

        self.env.models.pop('x_database.cleanup.test.model2')
        self.env._pure_function_fields.pop('x_database.cleanup.test.model2')


        #purge_models = self.env['cleanup.purge.wizard.model'].create({})
        #purge_models.purge_all()
        # must be removed by the wizard
        #self.assertFalse(self.env['ir.model'].search([
        #    ('model', '=', 'x_database.cleanup.test.model'),
        #]))

        return
        #self.env.cr.execute('select * from ir_model')

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

        '''
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


