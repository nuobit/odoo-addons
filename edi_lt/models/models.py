from openerp import models, fields, api, _

from openerp.exceptions import AccessError, Warning, ValidationError, except_orm

import base64
from lxml import etree
import ftplib
import StringIO

'''
class product_uom(models.Model):
    _inherit = "product.uom"

    edi_code = fields.Char(string='Edi code')

'''

class product_attribute_value(models.Model):
    _inherit = "product.attribute.value"

    edi_code = fields.Char(string='Edi code')




class purchase_order(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def edi_send(self):
        edilt = self.env['edilt.transaction'].search([('purchase_order_id', '=', self.id)])
        if not edilt:
            edilt = self.env['edilt.transaction'].create({'purchase_order_id': self.id})

        edilt.update()






class edilt_transaction(models.Model):
    _name = "edilt.transaction"

    purchase_order_id = fields.Many2one(string='Order', comodel_name='purchase.order', readonly=True)

    datas = fields.Binary(string='File', help="XML file")
    datas_fname = fields.Char(string='Filename')

    note = fields.Char(string='Note')

    last_conn_message = fields.Char(string='Last connexion message')

    state = fields.Selection(
        selection=[('pending', 'Pending'),
                   ('error', 'Error'),
                   ('done', 'Done'),
                   ],
        string='Status', default='pending', readonly=True,
        required=True)

    _sql_constraints = [('Unique purchase order', 'unique (purchase_order_id)', _('The transaction cannot have more than one purchase order'))]

    @api.multi
    def update(self):
        if self.state in ('pending', 'error'):
            xml = self.generate_xml()
            self.datas = base64.encodestring(xml)
            self.datas_fname = '%s.xml' % self.purchase_order_id.name.replace('/','').replace('\'','')

            server = self.env['edilt.server'].search([('default','=',True)])
            ftp = ftplib.FTP()
            ftp.connect(server.host, server.port)

            t = ftp.login(server.username, server.password)

            if server.folder:
                ftp.cwd(server.folder)

            t=ftp.pwd()


            try:
                #ftp.delete('oo')
                ftp.storbinary('STOR %s' % self.datas_fname, StringIO.StringIO(xml))


            except ftplib.all_errors as e:
                self.last_conn_message = e.message
                self.state = 'error'
                return self.show_message(e.message)
                #raise Warning(e.message)
            ftp.quit()



            #raise Warning(t)

        else:
            raise ValidationError(_('The transaction is already done'))

    def setElementText(self, elem, data, type='string', fmt='%(data)s', num_decimals=0, required=True):
        if (isinstance(data, bool) and not data) or data is None:
            if required:
                raise Warning(_('Element %s cannot be null') % elem.tag)
            return

        def format_date(obj, dt_str_utc):
            dt_utc = fields.Datetime.from_string(dt_str_utc)
            dt_loc = fields.Datetime.context_timestamp(obj, dt_utc)

            return dt_loc.strftime('%d/%m/%Y')

        def format_decimal(num, num_decimals, decimal_sep='.'):
            return ('{:.%if}' % num_decimals).format(num).replace(',', decimal_sep)

        def format_integer(num):
            return '{:d}'.format(num)

        format = {'string': lambda: fmt % dict(data=data), 'decimal': lambda: format_decimal(data, num_decimals),
                  'integer': lambda: format_integer(data), 'date': lambda: format_date(self, data)}

        elem.text = format[type]()

    def generate_xml(self):


        ## root
        InitialPurchaseOrder = etree.Element("InitialPurchaseOrder")

        #### level1
        PurchaseOrderHeader = etree.SubElement(InitialPurchaseOrder, "PurchaseOrderHeader")

        ####### level2
        IdSupplier = etree.SubElement(PurchaseOrderHeader, "IdSupplier")
        ######### level3
        SupplierName1 = etree.SubElement(IdSupplier, "SupplierName1")

        #SupplierName1.text = self.purchase_order_id.partner_id.name
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
        fmt = '%(data)s' + (' (%s)' % partner_id.comercial) if partner_id.comercial else ''
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
        so_name = self.purchase_order_id.origin
        so = self.env['sale.order'].search([('name', '=', so_name)])
        Reference.text = 'Order %s %s' % (so.client_order_ref, self.format_date(so.date_order))
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
        for ol in self.purchase_order_id.order_line.sorted(lambda x: x.id):
            for row_type in ('P', 'C'):
                IdRows = etree.SubElement(PurchaseOrderRows, "IdRows")

                RowNumber = etree.SubElement(IdRows, "RowNumber")
                self.setElementText(RowNumber, row_num, type='integer')
                if row_type == 'P':
                    RowProgressive = etree.SubElement(IdRows, "RowProgressive")
                    RowProgressive.text = '0'
                    RowType = etree.SubElement(IdRows, "RowType")
                    RowType.text = 'P'

                    if ol.product_id.product_tmpl_id.product_variant_count > 1:
                        item_code = '%s %s' % (ol.product_id.default_code, ol.product_id.attribute_value_ids[0].edi_code)
                    else:
                        item_code = ol.product_id.default_code

                    ItemReference = etree.SubElement(IdRows, "ItemReference")
                    ItemCode = etree.SubElement(IdRows, "ItemCode")
                    self.setElementText(ItemCode, item_code)
                    BarCode = etree.SubElement(IdRows, "BarCode")
                    self.setElementText(BarCode, ol.product_id.ean13)
                    Quantity = etree.SubElement(IdRows, "Quantity")
                    self.setElementText(Quantity, ol.product_qty, type='decimal', num_decimals=4)
                    UM = etree.SubElement(IdRows, "UM")
                    self.setElementText(UM, ol.with_context({'lang' : 'en_US'}).product_uom.name)
                    Description = etree.SubElement(IdRows, "Description")
                    self.setElementText(Description, ol.name)
                    UnitPrice = etree.SubElement(IdRows, "UnitPrice")
                    self.setElementText(UnitPrice, ol.price_unit, type='decimal', num_decimals=2)
                    Discount1 = etree.SubElement(IdRows, "Discount1")
                    self.setElementText(Discount1, ol.discount or 0, type='decimal', num_decimals=2)
                    Discount2 = etree.SubElement(IdRows, "Discount2")
                    self.setElementText(Discount2, 0, type='decimal', num_decimals=2)
                    Amount = etree.SubElement(IdRows, "Amount")
                    self.setElementText(Amount, ol.price_subtotal, type='decimal', num_decimals=2)
                    Currency = etree.SubElement(IdRows, "Currency")
                    self.setElementText(Currency, self.purchase_order_id.currency_id.name)

                    '''
                    if ol.taxes_id[0].child_ids:
                        for taxc in ol.taxes_id[0].child_ids:
                            if taxc.amount > 0:
                                taxpercent = taxc.amount
                                break
                    else:
                        taxpercent = ol.taxes_id[0].amount
                    '''
                    VatCode = etree.SubElement(IdRows, "VatCode")
                    #VatCode.text = self.format_float(taxpercent*100, 0)
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
                    self.setElementText(Currency, self.purchase_order_id.currency_id.name)
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

    def format_float(self, num, num_decimals, decimal_sep='.'):
        return ('{:.%if}' % num_decimals).format(num).replace(',', decimal_sep)

    def format_int(self, num):
        return '{:d}'.format(num)


    def show_message(self, message):
        wizard_id = self.env['edilt.message.info.wizard'].create({
            'message': message,
            })

        return {
            'type': 'ir.actions.act_window',
            'name': _("Info"),
            'res_model': 'edilt.message.info.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            #'views': [(view.id, 'form')],
            #'view_id': view.id,
            'res_id': wizard_id.id,
            'target': 'new',
            #'context': context,
        }


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




class edilt_message_info_wizard(models.TransientModel):
    _name = 'edilt.message.info.wizard'

    message = fields.Char(readonly=True)


