# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LightingProductAddAttachment(models.TransientModel):
    """
    This wizard will allow to attach multiple files at once
    """

    _name = "lighting.product.addattachment"
    _description = "Attach multiple files at once"

    name = fields.Char(string='Description', translate=True)
    type_id = fields.Many2one(comodel_name='lighting.attachment.type', ondelete='cascade', required=True,
                              string='Type')

    datas = fields.Binary(string="Document", attachment=True, required=True)
    datas_fname = fields.Char(string='Filename', required=True)

    lang_id = fields.Many2one(comodel_name='lighting.language', ondelete='cascade', string='Language')

    result = fields.Char(string='Result', readonly=True)

    state = fields.Selection([
        ('pending', 'Pending'),
        ('error', 'Error'),
        ('done', 'Done'),
    ], string='Status', default='pending', readonly=True, required=True, copy=False, track_visibility='onchange')

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '%s (%s)' % (record.datas_fname, record.type_id.display_name)
            vals.append((record.id, name))

        return vals

    @api.multi
    def add_attachment(self):
        reset_default_domain = ['|', ('res_field', '=', False), ('res_field', '!=', False)]

        # get wizard file hash
        addattach = self.env['ir.attachment'].search(
            reset_default_domain +
            [('res_model', '=', 'lighting.product.addattachment'), ('res_id', '=', self.id)]
        )

        # get products
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        products = self.env['lighting.product'].browse(active_ids)

        errors = {}
        for product in products:
            # check if attach already exists for the same file type
            for attach in product.attachment_ids:
                # get product attach object
                ir_attach = self.env['ir.attachment'].search(
                    reset_default_domain +
                        [('res_model', '=', 'lighting.attachment'), ('res_id', '=', attach.id)],
                    order='id'
                )

                if not ir_attach:
                    continue

                ir_attach = ir_attach[0]
                if ir_attach.checksum == addattach.checksum:
                    if product.id not in errors:
                        errors[product.id] = {'product': product}
                    if attach.type_id == self.type_id:
                        errors[product.id]['checksum_type'] = True
                        break
                    else:
                        if 'checksum_no_type' not in errors[product.id]:
                            errors[product.id]['checksum_no_type'] = []
                        errors[product.id]['checksum_no_type'].append(attach.type_id)

            if product.id not in errors:
                product.attachment_ids = [(0, False, {
                    'name': self.name,
                    'type_id': self.type_id.id,
                    'datas': self.datas,
                    'datas_fname': self.datas_fname,
                    'lang_id': self.lang_id.id,
                })]

        msg = []
        for data in errors.values():
            msg0 = []
            if 'checksum_type' in data:
                msg0.append(_('Already exists an attachment with the same type'))
            if 'checksum_no_type' in data:
                msg0.append(_('Already exists an attachment but with different types: %s') %
                            ', '.join({x.display_name for x in data['checksum_no_type']}))
            msg.append('> %s: %s' % (data['product'].reference, ', '.join(msg0)))

        if msg != []:
            msg = [_('Completed with ERRORS:')] + msg
            self.result = '\n'.join(msg)
            self.state = 'error'
        else:
            self.result = _('Completed without errors')
            self.state = 'done'

        return {
            'type': 'ir.actions.do_nothing'
        }
