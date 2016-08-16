from openerp import models, fields, api, _

from openerp.exceptions import AccessError, Warning, ValidationError, except_orm

import base64
from lxml import etree
import ftplib
import StringIO


class res_partner(models.Model):
    _inherit = "res.partner"

    is_edi = fields.Boolean(string='EDI', default=False)


class purchase_order(models.Model):
    _inherit = "purchase.order"

    is_edi = fields.Boolean(related='partner_id.is_edi')
    edi_transaction_id = fields.Many2one(string="EDI transaction", comodel_name='edilt.transaction',
                                         readonly=True, ondelete='restrict')

    @api.multi
    def edi_send(self):
        if not self.edi_transaction_id:
            self.edi_transaction_id = self.env['edilt.transaction'].create({'purchase_order_id': self.id})

        self.edi_transaction_id.set_filename()

        return self.edi_transaction_id.send()


    @api.multi
    def unlink(self):
        for rec in self:
            if rec.edi_transaction_id and rec.edi_transaction_id.state == 'done':
                raise ValidationError(_('You cannot delete a purchase order associated to a done EDI transaction'))
            super(purchase_order, rec).unlink()

    @api.multi
    def action_cancel(self):
        if self.edi_transaction_id and self.edi_transaction_id.state == 'done':
            raise ValidationError(_('You cannot cancel a purchase order associated to a done EDI transaction'))
        return super(purchase_order, self).action_cancel()


    @api.multi
    def action_picking_create(self):
        picking_id = super(purchase_order, self).action_picking_create()

        if self.related_usage == 'customer':
            picking_obj = self.env['stock.picking'].browse(picking_id)
            partner_id = self.dest_address_id
            if partner_id.parent_id:
                partner_id = partner_id.parent_id.partner_id

            picking_obj.partner_id = partner_id

        return picking_id




class edilt_transaction(models.Model):
    _name = "edilt.transaction"
    #_rec_name = 'datas_fname'

    name = fields.Char(string='Name', compute='_compute_name')

    purchase_order_id = fields.Many2one(string='Order', comodel_name='purchase.order', readonly=True, ondelete='cascade')

    datas = fields.Binary(string='File', help="XML file")
    datas_fname = fields.Char(string='Filename', required=True)

    trx_date = fields.Datetime('Transaction date', readonly=True)

    note = fields.Char(string='Note')

    state = fields.Selection(
        selection=[('pending', 'Pending'),
                   ('done', 'Done'),
                   ],
        string='Status', default='pending', readonly=True,
        required=True)

    _sql_constraints = [('Unique purchase order', 'unique (purchase_order_id)', _('The transaction cannot have more than one purchase order'))]

    @api.depends('purchase_order_id', 'state')
    def _compute_name(self):
        d = dict(self.fields_get('state')['state']['selection'])
        self.name = '%s (%s)' % (self.datas_fname, d[self.state])

    def set_filename(self):
        self.datas_fname = '%s.xml' % self.purchase_order_id.name.replace('/','').replace('\'','')

    @api.multi
    def send(self):
        if self.state in ('pending'):
            message = _('You are about to send the order directly to the supplier.\nThis operation is irreversible. Do you want to continue?')
            wizard_obj = self.env['edilt.message.acceptcancel.wizard'].create({
                'message': message,
                'edi_transaction_id': self.id,
                })

            return wizard_obj.run(title=_('Warning'))
        else:
            raise ValidationError(_('The purchase order has already been sent'))

    @api.multi
    def accept(self):
        xml_str = self.generate_xml()
        self.datas = base64.encodestring(xml_str)

        self.upload(xml_str, self.datas_fname)

        self.state = 'done'
        self.trx_date = fields.Datetime.now()

        self.purchase_order_id.message_post(body=_('EDI file %s sent') % self.datas_fname)


    @api.multi
    def set_to_pending(self):
        self.state='pending'

    @api.multi
    def delete(self):
        self.purchase_order_id.edi_transaction_id = False
        self.purchase_order_id = False
        self.unlink()


    @api.model
    def upload(self, xml_str, filename):
        server = self.env['edilt.server'].search([('default','=',True)])
        if not server:
            raise Warning(_("There's no default server configured"))
        if len(server)>1:
            raise Warning(_("There's more than one default server"))
        try:
            ftp = ftplib.FTP()
            ftp.connect(server.host, server.port)

            ftp.login(server.username, server.password)

            if server.folder:
                ftp.cwd(server.folder)

            #ftp.delete('oo')
            ftp.storbinary('STOR %s' % filename, StringIO.StringIO(xml_str))
            ftp.quit()
        except ftplib.all_errors as e:
            try:
                ftp.quit()
            except:
                pass

            raise Warning('FTP error: %s' % (e.message or e.strerror))

    def generate_xml(self):
        ## root
        InitialPurchaseOrder = etree.Element("InitialPurchaseOrder")

        #### level1
        PurchaseOrderHeader = etree.SubElement(InitialPurchaseOrder, "PurchaseOrderHeader")

        ####### level2
        IdSupplier = etree.SubElement(PurchaseOrderHeader, "IdSupplier")
        ######### level3
        SupplierName1 = etree.SubElement(IdSupplier, "SupplierName1")
        self.setElementText(SupplierName1, self.purchase_order_id.partner_id.name)
        SupplierName2 = etree.SubElement(IdSupplier, "SupplierName2")
        SupplierCode = etree.SubElement(IdSupplier, "SupplierCode")
        self.setElementText(SupplierCode, self.purchase_order_id.partner_id.ref, required=False)
        SupplierPostalCode = etree.SubElement(IdSupplier, "SupplierPostalCode")
        self.setElementText(SupplierPostalCode, self.purchase_order_id.partner_id.zip, required=False)
        SupplierLocality = etree.SubElement(IdSupplier, "SupplierLocality")
        self.setElementText(SupplierLocality, self.purchase_order_id.partner_id.city, required=False)
        SupplierProvince = etree.SubElement(IdSupplier, "SupplierProvince")
        self.setElementText(SupplierProvince, self.purchase_order_id.partner_id.state_id.name, required=False)

        IdDestination = etree.SubElement(PurchaseOrderHeader, "IdDestination")
        ######### level3
        if self.purchase_order_id.related_usage == 'customer':
            partner_id = self.purchase_order_id.dest_address_id
        else:
            partner_id = self.purchase_order_id.picking_type_id.warehouse_id.partner_id

        DestinationName1 = etree.SubElement(IdDestination, "DestinationName1")
        fmt = '%(data)s' + ((' (%s)' % partner_id.comercial) if partner_id.comercial else '')
        self.setElementText(DestinationName1, partner_id.name, fmt=fmt, required=True)

        DestinationName2 = etree.SubElement(IdDestination, "DestinationName2")
        self.setElementText(DestinationName2, partner_id.street2, required=False)
        DestinationAddress = etree.SubElement(IdDestination, "DestinationAddress")
        self.setElementText(DestinationAddress, partner_id.street)
        DestinationPostalCode = etree.SubElement(IdDestination, "DestinationPostalCode")
        self.setElementText(DestinationPostalCode, partner_id.zip, required=False)
        DestinationLocality = etree.SubElement(IdDestination, "DestinationLocality")
        self.setElementText(DestinationLocality, partner_id.city, required=False)
        DestinationProvince = etree.SubElement(IdDestination, "DestinationProvince")
        self.setElementText(DestinationProvince, partner_id.state_id.name, required=False)
        DestinationContry = etree.SubElement(IdDestination, "DestinationContry")
        self.setElementText(DestinationContry, partner_id.country_id.name, required=False)

        IdOrderData = etree.SubElement(PurchaseOrderHeader, "IdOrderData")
        ######### level3
        PurchaseOrder = etree.SubElement(IdOrderData, "PurchaseOrder")
        PurchaseOrder.text = 'Purchase order'
        PurchaseOrderNumber = etree.SubElement(IdOrderData, "PurchaseOrderNumber")
        self.setElementText(PurchaseOrderNumber, self.purchase_order_id.name)
        PurchaseOrderDate = etree.SubElement(IdOrderData, "PurchaseOrderDate")
        self.setElementText(PurchaseOrderDate, self.purchase_order_id.date_order, type='date')

        IdOther = etree.SubElement(PurchaseOrderHeader, "IdOther")
        ######### level3
        Reference = etree.SubElement(IdOther, "Reference")
        if self.purchase_order_id.related_usage == 'customer':
            so_origin_str = self.purchase_order_id.origin
            if not so_origin_str:
                raise Warning(_('A dropship purchase order must be linked to a sales order'))
            client_order_ref = []
            for so_name in [x.strip() for x in so_origin_str.split(',')]:
                so = self.env['sale.order'].search([('name', '=', so_name)])
                if not so:
                    raise Warning(_('The sale order %s does not exist') % so_name)
                if not so.client_order_ref or so.client_order_ref.strip() == '':
                    raise Warning(_('The sale order %s does not have a customer reference') % so_name)
                client_order_ref.append('%s (%s)' % (so.client_order_ref, self.format_date(so.date_order)))
            pl = 's' if len(client_order_ref)>1 else ''
            Reference.text = 'Order%s %s' % (pl, ', '.join(client_order_ref))

        DeliveryDate = etree.SubElement(IdOther, "DeliveryDate")
        self.setElementText(DeliveryDate, self.purchase_order_id.minimum_planned_date, type='date')
        PaymentCode = etree.SubElement(IdOther, "PaymentCode")
        PaymentDescription = etree.SubElement(IdOther, "PaymentDescription")
        MadeGoodsCode = etree.SubElement(IdOther, "MadeGoodsCode")
        MadeGoodsDescription = etree.SubElement(IdOther, "MadeGoodsDescription")
        ShipmentCode = etree.SubElement(IdOther, "ShipmentCode")
        Shipment = etree.SubElement(IdOther, "Shipment")
        DeliveryCode = etree.SubElement(IdOther, "DeliveryCode")
        DeliveryDescription = etree.SubElement(IdOther, "DeliveryDescription")

        #### level1
        PurchaseOrderRows = etree.SubElement(InitialPurchaseOrder, "PurchaseOrderRows")
        ####### level2
        row_num = 10
        for i, ol in enumerate(self.purchase_order_id.order_line.sorted(lambda x: x.id),1):
            for row_type in ('P', 'C'):
                IdRows = etree.SubElement(PurchaseOrderRows, "IdRows")

                RowNumber = etree.SubElement(IdRows, "RowNumber")
                self.setElementText(RowNumber, row_num, type='integer')
                if row_type == 'P':
                    RowProgressive = etree.SubElement(IdRows, "RowProgressive")
                    RowProgressive.text = '0'
                    RowType = etree.SubElement(IdRows, "RowType")
                    RowType.text = 'P'

                    ItemReference = etree.SubElement(IdRows, "ItemReference")
                    ItemCode = etree.SubElement(IdRows, "ItemCode")
                    self.setElementText(ItemCode, ol.product_id.default_code, line=i)
                    BarCode = etree.SubElement(IdRows, "BarCode")
                    self.setElementText(BarCode, ol.product_id.ean13, line=i)
                    Quantity = etree.SubElement(IdRows, "Quantity")
                    self.setElementText(Quantity, ol.product_qty, type='decimal', num_decimals=4, line=i)
                    UM = etree.SubElement(IdRows, "UM")
                    self.setElementText(UM, ol.with_context({'lang' : 'en_US'}).product_uom.name, line=i)
                    Description = etree.SubElement(IdRows, "Description")
                    self.setElementText(Description, ol.name, line=i)
                    UnitPrice = etree.SubElement(IdRows, "UnitPrice")
                    self.setElementText(UnitPrice, ol.price_unit, type='decimal', num_decimals=2, line=i)
                    Discount1 = etree.SubElement(IdRows, "Discount1")
                    self.setElementText(Discount1, ol.discount or 0, type='decimal', num_decimals=2, line=i)
                    Discount2 = etree.SubElement(IdRows, "Discount2")
                    self.setElementText(Discount2, 0, type='decimal', num_decimals=2, line=i)
                    Amount = etree.SubElement(IdRows, "Amount")
                    self.setElementText(Amount, ol.price_subtotal, type='decimal', num_decimals=2, line=i)
                    Currency = etree.SubElement(IdRows, "Currency")
                    self.setElementText(Currency, self.purchase_order_id.currency_id.name, line=i)
                    VatCode = etree.SubElement(IdRows, "VatCode")
                elif row_type == 'C':
                    RowProgressive = etree.SubElement(IdRows, "RowProgressive")
                    RowProgressive.text = '1'
                    RowType = etree.SubElement(IdRows, "RowType")
                    RowType.text = 'C'
                    Description = etree.SubElement(IdRows, "Description")
                    Discount1 = etree.SubElement(IdRows, "Discount1")
                    self.setElementText(Discount1, 0, type='decimal', num_decimals=2)
                    Discount2 = etree.SubElement(IdRows, "Discount2")
                    self.setElementText(Discount2, 0, type='decimal', num_decimals=2)
                    Amount = etree.SubElement(IdRows, "Amount")
                    self.setElementText(Amount, 0, type='decimal', num_decimals=2)
                    Currency = etree.SubElement(IdRows, "Currency")
                    self.setElementText(Currency, self.purchase_order_id.currency_id.name, line=i)
                    VatCode = etree.SubElement(IdRows, "VatCode")

            row_num += 20

        #### level1
        PurchaseOrderFooters = etree.SubElement(InitialPurchaseOrder, "PurchaseOrderFooters")

        ####### level2
        IdFooters  = etree.SubElement(PurchaseOrderFooters, "IdFooters")
        ######### level3
        Annotation = etree.SubElement(IdFooters, "Annotation")
        FinalAmount = etree.SubElement(IdFooters, "FinalAmount")
        self.setElementText(FinalAmount, self.purchase_order_id.amount_total, type='decimal', num_decimals=2)
        Currency = etree.SubElement(IdFooters, "Currency")
        self.setElementText(Currency, self.purchase_order_id.currency_id.name)

        xml_text = etree.tostring(InitialPurchaseOrder, encoding='UTF-8', method='xml', xml_declaration = True, pretty_print=True)

        return xml_text


    def format_date(self, dt_str_utc):
        dt_utc = fields.Datetime.from_string(dt_str_utc)
        dt_loc = fields.Datetime.context_timestamp(self, dt_utc)

        return dt_loc.strftime('%d/%m/%Y')

    def format_decimal(self, num, num_decimals, decimal_sep='.'):
        return ('{:.%if}' % num_decimals).format(num).replace(',', decimal_sep)

    def format_integer(self, num):
        return '{:d}'.format(num)


    def setElementText(self, elem, data, type='string', fmt='%(data)s', num_decimals=0, required=True, line=None):
        if (isinstance(data, bool) and not data) or data is None:
            if required:
                err_msg = _('Element %s cannot be null') % elem.tag
                if line is not None:
                    err_msg = _('Line %i: %s') % (line, err_msg)
                raise Warning(err_msg)
            return

        format = {'string': lambda: fmt % dict(data=data), 'decimal': lambda: self.format_decimal(data, num_decimals),
                  'integer': lambda: self.format_integer(data), 'date': lambda: self.format_date(data)}

        elem.text = format[type]()


class edilt_server(models.Model):
    _name = "edilt.server"

    name = fields.Char('Name', required=True)
    type = fields.Selection(string='Type', selection=[('ftp', 'FTP')], required=True, default='ftp')
    host = fields.Char('Host', required=True)
    port = fields.Integer('Port', required=True, default=21)

    folder = fields.Char('Folder')

    username = fields.Char('Username', required=True)
    password = fields.Char('Password', required=True)

    default = fields.Boolean('Default', default=lambda self: self._default_default())


    def _default_default(self):
        s = self.env['edilt.server'].search_count([])

        return s==1

    @api.constrains('default')
    def _constraint_default(self):
        if self.default:
            self.env['edilt.server'].search([('id', '!=', self.id)]).default=False




class edilt_message_info_wizard(models.TransientModel):
    _name = 'edilt.message.info.wizard'

    message = fields.Char(readonly=True)

    def run(self, title="Warning"):
        return {
                'type': 'ir.actions.act_window',
                'name': title,
                'res_model': 'edilt.message.info.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                #'views': [(view.id, 'form')],
                #'view_id': view.id,
                'res_id': self.id,
                'target': 'new',
                #'context': context,
            }


class edilt_message_acceptcancel_wizard(models.TransientModel):
    _name = 'edilt.message.acceptcancel.wizard'

    message = fields.Char(readonly=True)
    edi_transaction_id = fields.Many2one(string="EDI transaction", comodel_name='edilt.transaction',
                                         readonly=True)

    def run(self, title="Warning"):
        return {
                'type': 'ir.actions.act_window',
                'name': title,
                'res_model': 'edilt.message.acceptcancel.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                #'views': [(view.id, 'form')],
                #'view_id': view.id,
                'res_id': self.id,
                'target': 'new',
                #'context': context,
            }

    @api.multi
    def accept(self):
        self.edi_transaction_id.accept()

        message = _('Operation completed successfully')
        wizard_obj = self.env['edilt.message.info.wizard'].create({
                'message': message,
                })

        return wizard_obj.run(title=_('Info'))





