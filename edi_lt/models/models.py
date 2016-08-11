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

    def generate_xml(self):
        ## root
        InitialPurchaseOrder = etree.Element("InitialPurchaseOrder")

        #### level1
        PurchaseOrderHeader = etree.SubElement(InitialPurchaseOrder, "PurchaseOrderHeader")

        ####### level2
        IdSupplier = etree.SubElement(PurchaseOrderHeader, "IdSupplier")
        ######### level3
        SupplierName1 = etree.SubElement(IdSupplier, "SupplierName1")
        SupplierName1.text = self.purchase_order_id.partner_id.name
        SupplierName2 = etree.SubElement(IdSupplier, "SupplierName2")
        SupplierCode = etree.SubElement(IdSupplier, "SupplierCode")
        SupplierCode.text = self.purchase_order_id.partner_id.ref or None
        SupplierPostalCode = etree.SubElement(IdSupplier, "SupplierPostalCode")
        SupplierPostalCode.text = self.purchase_order_id.partner_id.zip or None
        SupplierLocality = etree.SubElement(IdSupplier, "SupplierLocality")
        SupplierLocality.text = self.purchase_order_id.partner_id.city or None

        SupplierProvince = etree.SubElement(IdSupplier, "SupplierProvince")
        SupplierProvince.text = self.purchase_order_id.partner_id.state_id.name or None

        IdDestination = etree.SubElement(PurchaseOrderHeader, "IdDestination")
        ######### level3
        if self.purchase_order_id.related_usage == 'customer':
            partner_id = self.purchase_order_id.dest_address_id
        else:
            partner_id = self.purchase_order_id.picking_type_id.warehouse_id.partner_id

        DestinationName1 = etree.SubElement(IdDestination, "DestinationName1")
        DestinationName1.text = '%s%s' % (partner_id.name, '(%s)' % partner_id.comercial if partner_id.comercial else '')
        DestinationName2 = etree.SubElement(IdDestination, "DestinationName2")
        DestinationName2.text = partner_id.street2 or None
        DestinationAddress = etree.SubElement(IdDestination, "DestinationAddress")
        DestinationAddress.text = partner_id.street
        DestinationPostalCode = etree.SubElement(IdDestination, "DestinationPostalCode")
        DestinationPostalCode.text = partner_id.zip or None
        DestinationLocality = etree.SubElement(IdDestination, "DestinationLocality")
        DestinationLocality.text = partner_id.city or None
        DestinationProvince = etree.SubElement(IdDestination, "DestinationProvince")
        DestinationProvince.text = partner_id.state_id.name or None
        DestinationContry = etree.SubElement(IdDestination, "DestinationContry")
        DestinationContry.text = partner_id.country_id.name or None

        IdOrderData = etree.SubElement(PurchaseOrderHeader, "IdOrderData")
        ######### level3
        PurchaseOrder = etree.SubElement(IdOrderData, "PurchaseOrder")
        PurchaseOrder.text = 'Purchase order'
        PurchaseOrderNumber = etree.SubElement(IdOrderData, "PurchaseOrderNumber")
        PurchaseOrderNumber.text = self.purchase_order_id.name
        PurchaseOrderDate = etree.SubElement(IdOrderData, "PurchaseOrderDate")
        PurchaseOrderDate.text = self.format_date(self.purchase_order_id.date_order)

        IdOther = etree.SubElement(PurchaseOrderHeader, "IdOther")
        ######### level3
        Reference = etree.SubElement(IdOther, "Reference")
        so_name = self.purchase_order_id.origin
        so = self.env['sale.order'].search([('name', '=', so_name)])
        Reference.text = 'Order %s %s' % (so.client_order_ref, self.format_date(so.date_order))
        DeliveryDate = etree.SubElement(IdOther, "DeliveryDate")
        DeliveryDate.text = self.format_date(self.purchase_order_id.minimum_planned_date)
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
                RowNumber.text = self.format_int(row_num)
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
                    ItemCode.text = item_code
                    BarCode = etree.SubElement(IdRows, "BarCode")
                    BarCode.text = ol.product_id.ean13
                    Quantity = etree.SubElement(IdRows, "Quantity")
                    Quantity.text = self.format_float(ol.product_qty, 4)
                    UM = etree.SubElement(IdRows, "UM")
                    UM.text = ol.with_context({'lang' : 'en_US'}).product_uom.name
                    Description = etree.SubElement(IdRows, "Description")
                    Description.text = ol.name
                    UnitPrice = etree.SubElement(IdRows, "UnitPrice")
                    UnitPrice.text = self.format_float(ol.price_unit, 2)
                    Discount1 = etree.SubElement(IdRows, "Discount1")
                    Discount1.text = self.format_float(ol.discount or 0, 2)
                    Discount2 = etree.SubElement(IdRows, "Discount2")
                    Discount2.text = self.format_float(0, 2)
                    Amount = etree.SubElement(IdRows, "Amount")
                    Amount.text = self.format_float(ol.price_subtotal, 2)
                    Currency = etree.SubElement(IdRows, "Currency")
                    Currency.text = self.purchase_order_id.currency_id.name

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
                    Discount1.text = self.format_float(0, 2)
                    Discount2 = etree.SubElement(IdRows, "Discount2")
                    Discount2.text = self.format_float(0, 2)
                    Amount = etree.SubElement(IdRows, "Amount")
                    Amount.text = self.format_float(0, 2)
                    Currency = etree.SubElement(IdRows, "Currency")
                    Currency.text = self.purchase_order_id.currency_id.name
                    VatCode = etree.SubElement(IdRows, "VatCode")

            row_num += 20


        #### level1
        PurchaseOrderFooters = etree.SubElement(InitialPurchaseOrder, "PurchaseOrderFooters")

        ####### level2
        IdFooters  = etree.SubElement(PurchaseOrderFooters, "IdFooters")
        ######### level3
        Annotation = etree.SubElement(IdFooters, "Annotation")
        FinalAmount = etree.SubElement(IdFooters, "FinalAmount")
        FinalAmount.text = self.format_float(self.purchase_order_id.amount_total, 2)
        Currency = etree.SubElement(IdFooters, "Currency")
        Currency.text = self.purchase_order_id.currency_id.name

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


