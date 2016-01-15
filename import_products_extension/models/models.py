# -*- coding: utf-8 -*-
#/#############################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2015 NuoBiT Solutions, S.L. (<http://www.nuobit.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#/#############################################################################



from datetime import timedelta

import pytz

import base64
import StringIO
import re
import csv
import unicodedata
import string

import decimal

from openerp import models, fields, api, _
from openerp.exceptions import AccessError, Warning, ValidationError

from openerp.addons.product.product import check_ean



import logging

_logger = logging.getLogger(__name__)


class import_header(models.Model):
    """Session"""
    _name = 'epe.header'
    _description = 'Header'

    name = fields.Char(string='Description', required=False,
        readonly=False)

    date_import = fields.Datetime('Date', required=True, default=fields.datetime.now())

    supplier_id = fields.Many2one('res.partner', string="Supplier", domain=[('supplier','=', True)])

    delimiter = fields.Char(string='Delimitar', required=True,
        readonly=False, default=',')
    quotechar = fields.Char(string='Quotechar', required=True,
        readonly=False, default='"')

    strip_fields = fields.Boolean(string='Strip values',
        help="Remove trail and leading spaces of each field",
        readonly=False, default=True)

    round_numeric_fields = fields.Integer(string='Round',
        help="Round numeric values to this number of decimals. -1 or any negative number to not round at all",
        readonly=False, default=2)


    update_name = fields.Boolean(string='Update Description',
        help="Update Description when importing data",
        readonly=False, default=False)

    update_ean13 = fields.Boolean(string='Update EAN',
        help="Update EAN 13 when importing data",
        readonly=False, default=False)

    update_saleprice = fields.Boolean(string='Update Sale Price',
        help="Update Sale Pricelist when importing data",
        readonly=False, default=False)

    update_purchaseprice = fields.Boolean(string='Update Purchase Price',
        help="Update Purchase Pricelist when importing data",
        readonly=False, default=True)

    update_category = fields.Boolean(string='Update Category',
        help="Update Category if exists",
        readonly=False, default=False)


    create_product = fields.Boolean(string='Create Product',
        help="Create Product if not exists",
        readonly=False, default=False)

    create_category_onupdate = fields.Boolean(string='Create Category',
        help="If 'Update Category' is selected create Category if not exists. If 'Update Category' is not selected it has no effect",
        readonly=False, default=False)

    create_category_oncreate = fields.Boolean(string='Create Category',
        help="Create Category if not exists",
        readonly=False, default=False)

    create_supplier = fields.Boolean(string='Create always Supplier Info',
        help="Create Supplier Info although Purchase Pricelist is null",
        readonly=False, default=False)


    sale_delay = fields.Float(string='Customer Lead Time', required=True,
        readonly=False, default=0)

    purchase_delay = fields.Float(string='Delivery Lead Time', required=True,
        readonly=False, default=0)

    product_type = fields.Selection([('product', 'Stockable Product'), ('consu', 'Consumable'), ('service', 'Service')],
        'Product Type', required=True, default='product',
        help="Consumable: Will not imply stock management for this product. \nStockable product: Will imply stock management for this product.")

    cost_method = fields.Selection(type='selection', selection=[('standard', 'Standard Price'), ('average', 'Average Price'), ('real', 'Real Price')],
            help="Standard Price: The cost price is manually updated at the end of a specific period (usually every year).\nAverage Price: The cost price is recomputed at each incoming shipment and used for the product valuation.\nReal Price: The cost price displayed is the price of the last outgoing product (will be use in case of inventory loss for example).",
            string="Costing Method", required=True, copy=True, default='average')


    datas = fields.Binary('File')
    datas_fname = fields.Char(string='Filename')

    line_ids = fields.One2many('epe.line','header_id')



    def _split_line(self, line):
        line9 = []
        for line in csv.reader([line],delimiter=self.delimiter.encode(), quotechar=self.quotechar.encode()):
            line9.append(line)
        return line9[0]


    @api.multi
    def load_file(self):
        self.line_ids.unlink()

        txt = base64.decodestring(self.datas)
        # remove lasts newlines
        txt = re.sub(r'\n*$','' ,txt,flags=re.DOTALL)

        for i, line in enumerate(txt.split('\n')):
            field_values = [x.strip() if self.strip_fields else x for x in self._split_line(line)]
            if i==0:
                header = field_values
            else:
                if len(header)!=len(field_values):
                    raise Warning(_("Incorrect field number in line %i") % i+1)
                field_values = [x if x!='' else None for x in field_values]
                fields = dict(zip(header, field_values))
                fields.update(header_id=self.id)
                self.env['epe.line'].create(fields)

    @api.multi
    def clear(self):
        self.line_ids.unlink()

    @api.multi
    def remove_done(self):
        for line in self.line_ids:
            if line.status == 'done':
                line.unlink()

    def _check_float_format(self, r):
        v = None

        if re.search('^[0-9]+$', r) is not None:
            v = r
        if re.search('^[0-9]+,[0-9]+$', r) is not None:
            v = r.replace(',','.')
        elif re.search('^[0-9]+\.[0-9]+$', r) is not None:
            v = r
        elif re.search('^[0-9]+\.[0-9]+,[0-9]+$', r) is not None:
            v = r.replace('.','').replace(',','.')
        elif re.search('^[0-9]+,[0-9]+\.[0-9]+$', r) is not None:
            v = r.replace(',','')

        return v

    def _format_decimal(self, d, ret_type='float'):
        f = decimal.Decimal(d)
        if self.round_numeric_fields:
            f = decimal.Decimal(f.quantize(decimal.Decimal('0.%s1' % '0'* (self.round_numeric_fields-1)), rounding=decimal.ROUND_HALF_EVEN))
        if ret_type=='text':
            f=str(f)
        elif ret_type=='float':
            float(f)
        return f

    def _float2decimal(self, d):
        return decimal.Decimal(d).quantize(decimal.Decimal('0.00000000001'))

    def _slugify(self, r):
        return ''.join(x for x in unicodedata.normalize('NFKD', r) if x in string.ascii_letters).lower()

    def _equal(self, a, b):
        pass


    def _get_cat(self, line):
        status = None
        cat, cat_status, cat_msg = None, None, False
        nc = []
        for cat in self.env['product.category'].search([]):
            if self._slugify(cat.name)==self._slugify(line.category):
                nc.append(cat)
        if len(nc)==0:
            cat_langs = self.env['ir.translation'].search([('lang','!=', self._context['lang']),
                ('res_id','=', cat.id),('name', '=', 'product.category,name')])
            nl = []
            nls = []
            has_en_us = False
            for cl in cat_langs:
                if cl.lang=='en_US':
                    has_en_us = True
                if self._slugify(cl.value)==self._slugify(line.category):
                    nl.append(cl)
                nls.append(cl.src)

            src = None
            snls = list(set(nls))
            if len(snls)>1:
                line.status='error'
                line.observations=_("There's more than one translation sources with different source")
                status = 'error'
                #continue
            elif len(snls)==1:
                src = snls[0]

            if len(nl)==0:
                if src is not None and not has_en_us:
                    if self._slugify(src)==self._slugify(line.category):
                        line.status='error'
                        line.observations=_("Exists an english source with the Category but explicit english language is not defined")
                        status = 'error'
                        #continue
                cat_msg=_('Category did not exist, it was created')
                cat_status = 'create'
            else:
                nll = [x.lang for x in nl]
                line.status='error'
                line.observations=_("Current language '%s' does not have that Category but other languages do: '%s'") % (self._context['lang'], nll )
                status = 'error'
                #continue
        elif len(nc)==1:
            if self._slugify(nc[0].name)!=self._slugify(line.category):
                cat_msg = _("Used category %s instead of %s") % (nc[0].name, line.category)
                line.category = nc[0].name
            cat_status = 'exists'
            cat = nc[0]
        else:
            line.status='error'
            line.observations=_("There's more than one category with the same slug %s") % nc
            status = 'error'

        return status, cat, cat_status, cat_msg


    @api.onchange('show_status')
    #@api.multi
    def onchange_status(self):
        fs1 = self.line_ids.filtered(lambda x: x.status==self.show_status).mapped('id')
        res = {'line_ids': [('id', 'in', fs1)]}

        return dict(domain=res)


    @api.multi
    def update(self):
        n = len(self.line_ids)
        pco = None
        for i, line in enumerate(self.line_ids):
            if n!=1:
                pc = float(i)/(float(n)-1)*100.0
            else:
                pc = 100.0
            if int(pc)!=pco:
                #if (int(pc) % 10) == 0:
                _logger.info('Import progress %.2f%%' % pc)
            pco = int(pc)

            if line.status=='done':
                continue

            line.status = False
            line.observations = False

            # check if product exists (defualt_code)
            if not line.default_code:
                line.status='error'
                line.observations=_("Reference cannot be null")
                continue

            product = {}
            pp = self.env['product.product'].search([('default_code','=', line.default_code)])
            if len(pp)>1:
                line.status='error'
                line.observations=_("There's more than one product with the same Reference")
                continue
            else:
                product['status'] = 'update' if len(pp)==1 else 'create'

            # check pricelist_sale
            if line.pricelist_sale:
                price = self._check_float_format(line.pricelist_sale)
                if price is None:
                    line.status='error'
                    line.observations=_('Unknown float format')
                    continue
                else:
                    line.pricelist_sale = self._format_decimal(price, ret_type='text')

            # check purchase priceist
            if line.pricelist_purchase:
                price = self._check_float_format(line.pricelist_purchase)
                if price is None:
                    line.status='error'
                    line.observations=_('Unknown float format')
                    continue
                else:
                    line.pricelist_purchase = self._format_decimal(price, ret_type='text')

            ## populate data
            product['data'] = {}
            if product['status'] == 'update':
                product['object'] = pp
                if self.update_name:
                    if line.name:
                        if pp.name!=pp.name:
                            product['data'].update({'name': line.name })
                    # TODO: Update name on every language
                if self.update_ean13:
                    if line.ean13:
                        if pp.ean13!=line.ean13:
                            if check_ean(line.ean13):
                                product['data'].update({'ean13': line.ean13 })
                            else:
                                line.status='error'
                                line.observations=_('Invalid "EAN13 Barcode"')
                                continue
                if self.update_saleprice:
                    if line.pricelist_sale:
                        pricelist_sale = self._format_decimal(line.pricelist_sale)
                        if self._float2decimal(pp.lst_price)!=pricelist_sale:
                            product['data'].update({'lst_price': float(pricelist_sale) })
                if self.update_purchaseprice:
                    if line.pricelist_purchase:
                        if not self.supplier_id.id:
                            line.status='error'
                            line.observations=_('If there is a Purchase Pricelist the Supplier cannot be null')
                            continue
                        else:
                            suppinfo = pp.seller_ids.filtered(lambda x: x.name==self.supplier_id)
                            if len(suppinfo)>1:
                                line.status='error'
                                line.observations=_('There is more then one Supplier defined')
                                continue
                            elif len(suppinfo)==0:
                                product['data'].update({'seller_ids': [(0,_, {'name': self.supplier_id.id, 'delay': self.purchase_delay,
                                                                          'pricelist_ids': [(0,_,{'min_quantity': 0,
                                                                                                  'price': float(self._format_decimal(line.pricelist_purchase))})]})]})
                            else:
                                plist = suppinfo.pricelist_ids
                                if len(plist)>1:
                                    plist0 = plist.filtered(lambda x: x.min_quantity==0)
                                    line.status='error'
                                    line.observations=_('There is more than one Purchase Pricelist')
                                    if len(plist0)==0:
                                        line.observations+=_(' and none has quantity=0')
                                    elif len(plist0)==1:
                                        line.observations=_(' and just one has quantity=0')
                                    else:
                                        line.observations=_(' and more than one has quantity=0')
                                    continue
                                elif len(plist)==0:
                                    product['data'].update({'seller_ids': [(1, suppinfo.id, {
                                                                          'pricelist_ids': [(0,_,{'min_quantity': 0,
                                                                                                  'price': float(self._format_decimal(line.pricelist_purchase))})]})]})
                                else:
                                    pricelist_purchase = self._format_decimal(line.pricelist_purchase)
                                    old_pricelist_purchase = self._float2decimal(pp.seller_ids.filtered(lambda x: x.id==suppinfo.id).mapped('pricelist_ids').filtered(lambda x: x.id==plist.id).price)
                                    if pricelist_purchase!=old_pricelist_purchase:
                                        product['data'].update({'seller_ids': [(1, suppinfo.id, {
                                                                          'pricelist_ids': [(1, plist.id, {'price': float(pricelist_purchase)})]})]})
                if self.update_category:
                    status, cat, cat_status, cat_msg = self._get_cat(line)
                    if status=='error':
                        continue
                    if cat_status == 'exists':
                        if pp.categ_id!=cat.id:
                            product['data'].update({'categ_id': cat.id})
                            line.observations = cat_msg
                    else:
                        if self.create_category_onupdate:
                            product['category']={'status': 'create', 'data': {'name': line.category}}
                            line.observations = cat_msg
                        else:
                            line.status = 'error'
                            line.observations=_('Category did not exist. Enable "Create Category" on update options to create it')
                            continue
            else:
                if not self.create_product:
                    line.status = 'pending'
                    line.observations = _("Product does not exist. Enable 'Create Product' to create it")
                    continue
                product['data'].update({'default_code': line.default_code,
                                        'sale_delay': self.sale_delay, 'type': self.product_type,
                                        'cost_method': self.cost_method })
                if not line.name:
                    line.status='error'
                    line.observations=_('Description cannot be null')
                    continue
                else:
                    product['data'].update({'name': line.name})
                if line.ean13:
                    if check_ean(line.ean13):
                        product['data'].update({'ean13': line.ean13 })
                    else:
                        line.status='error'
                        line.observations=_('Invalid "EAN13 Barcode"')
                        continue

                status, cat, cat_status, cat_msg = self._get_cat(line)
                if status=='error':
                    continue
                if cat_status == 'exists':
                    product['data'].update({'categ_id': cat.id})
                    line.observations = cat_msg
                else:
                    if self.create_category_oncreate:
                        product['category']={'status': 'create', 'data': {'name': line.category}}
                        line.observations = cat_msg
                    else:
                        line.status = 'error'
                        line.observations=_('Category did not exist. Enable "Create Category" on create options to create it')
                        continue

                if not line.pricelist_sale:
                    product['data'].update({'lst_price': 0 })
                else:
                    product['data'].update({'lst_price': float(self._format_decimal(line.pricelist_sale)) })

                if not line.pricelist_purchase:
                    if self.supplier_id.id:
                        if self.create_supplier:
                            product['data'].update({'seller_ids': [(0,_, {'name': self.supplier_id.id, 'delay': self.purchase_delay })]})
                else:
                    if not self.supplier_id.id:
                        line.status='error'
                        line.observations=_('If there is a Purchase Pricelist the Supplier cannot be null')
                        continue
                    else:
                        product['data'].update({'seller_ids': [(0,_, {'name': self.supplier_id.id, 'delay': self.purchase_delay,
                                                                      'pricelist_ids': [(0,_,{'min_quantity': 0,
                                                                                'price': float(self._format_decimal(line.pricelist_purchase))})]})]})
            ## save data
            cat = None
            if product.get('category') is not None:
                if product['category']['status']=='create':
                    cat = self.env['product.category'].create(product['category']['data'])
                    product['data'].update({'categ_id': cat.id})

            if product['status']=='update':
                if product['data'] != {}:
                    product['object'].write(product['data'])
                else:
                    line.observations = _("Nothing changed. Data already updated")
            else:
                self.env['product.product'].create(product['data'])

            line.status = 'done'








    '''
    def import_file(self, cr, uid, ids, context=None):
    fileobj = TemporaryFile('w+')
    fileobj.write(base64.decodestring(data))

    # your treatment
    return
    '''
    '''
        if context is None:
            context = {}
        result = {}
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            if attach.store_fname:
                result[attach.id] = self._file_read(cr, uid, attach.store_fname, bin_size)
            else:
                result[attach.id] = attach.db_datas
        return result

    def _file_read(self, cr, uid, fname, bin_size=False):
        full_path = self._full_path(cr, uid, fname)
        r = ''
        try:
            if bin_size:
                r = os.path.getsize(full_path)
            else:
                r = open(full_path,'rb').read().encode('base64')
        except IOError:
            _logger.exception("_read_file reading %s", full_path)
        return r

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        # We dont handle setting data to null
        if not value:
            return True
        if context is None:
            context = {}
        location = self._storage(cr, uid, context)
        file_size = len(value.decode('base64'))
        attach = self.browse(cr, uid, id, context=context)
        fname_to_delete = attach.store_fname
        if location != 'db':
            fname = self._file_write(cr, uid, value)
            # SUPERUSER_ID as probably don't have write access, trigger during create
            super(ir_attachment, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size, 'db_datas': False}, context=context)
        else:
            super(ir_attachment, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size, 'store_fname': False}, context=context)

        # After de-referencing the file in the database, check whether we need
        # to garbage-collect it on the filesystem
        if fname_to_delete:
            self._file_delete(cr, uid, fname_to_delete)
        return True
    '''



class import_lines(models.Model):
    """Session"""
    _name = 'epe.line'
    _description = 'Import Lines'

    default_code = fields.Char(string='Reference', required=True)

    name = fields.Char(string='Description', required=False,
        readonly=False)

    category = fields.Char(string='Category', required=False,
        readonly=False)

    ean13 = fields.Char(string='EAN', required=False,
        readonly=False)

    pricelist_sale = fields.Char(string="Sale Pricelist", required=False)
    pricelist_purchase = fields.Char(string="Purchase Pricelist", required=False)

    header_id = fields.Many2one('epe.header', required=True, ondelete="cascade")

    status = fields.Selection([('done',_('Done')),('error',_('Error')), ('pending', _('Pending'))], string="Status")
    observations = fields.Text(string='Observations',
        readonly=True)

