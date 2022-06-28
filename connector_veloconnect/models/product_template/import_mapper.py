# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
import base64
import hashlib
import requests
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, only_create)
from odoo.addons.connector_veloconnect.models.common import tools
from odoo.odoo import fields
from odoo.odoo.exceptions import ValidationError


class ProductTemplateImportMapChild(Component):
    _name = 'veloconnect.product.template.map.child.import'
    _inherit = 'veloconnect.map.child.import'

    _apply_on = 'veloconnect.product.supplierinfo'

    # def get_item_values(self, map_record, to_attr, options):
    #     binder = self.binder_for('veloconnect.product.supplierinfo')
    #     external_id = binder.dict2id(map_record.source, in_field=False)
    #     binding = binder.to_internal(external_id, unwrap=False)
    #     # if not binding:
    #     #     record = binder._to_record_from_external_key(map_record)
    #     #     if record:
    #     #         map_record.update({
    #     #             binder._odoo_field: record.id
    #     #         })
    #     # else:
    #     #     map_record.update(id=binding.id)
    #     if binding:
    #         map_record.update(id=binding.id)
    #     return map_record.values(**options)


class VeloconnectProductTemplateImportMapper(Component):
    _name = 'veloconnect.product.template.import.mapper'
    _inherit = 'veloconnect.import.mapper'

    _apply_on = 'veloconnect.product.template'

    direct = []

    children = [('items', 'veloconnect_seller_ids', 'veloconnect.product.supplierinfo')]

    @only_create
    @mapping
    def barcode(self, record):
        return {'barcode': record['StandardItemIdentification']}

    @only_create
    @mapping
    def name(self, record):
        if record['Description'] is None:
            return None
        return {'name': record['Description']}

    @mapping
    def price(self, record):
        binding = self.options.get("binding")
        other_bindings = binding.veloconnect_bind_ids.filtered(lambda x: x.backend_id != self.backend_record)
        max_price = max([x.veloconnect_price for x in other_bindings] + [record['RecommendedRetailPrice']])
        return {'list_price': max_price}

    @mapping
    def binding_description(self, record):
        return {'veloconnect_description': record['Description']}

    @mapping
    def binding_price(self, record):
        return {'veloconnect_price': record['RecommendedRetailPrice']}

    @mapping
    def binding_uom(self, record):
        return {'veloconnect_uom': record['quantityUnitCode']}

    @mapping
    def default_code(self, record):
        manufacturer_id = record.get('ManufacturersItemIdentificationID')
        if manufacturer_id:
            binding = self.options.get("binding")
            if not binding or not binding.default_code:
                return {'default_code': manufacturer_id}

    @mapping
    def hash(self, record):
        return {'veloconnect_hash': record['Hash']}

    @mapping
    def product_brand_id(self, record):
        brand_name = record.get('ManufacturersItemIdentificationName')
        if brand_name:
            binding = self.options.get("binding")
            if not binding or not binding.product_brand_id:
                name_slug = tools.slugify(brand_name)
                brand = self.env['product.brand'].search([('name_slug', '=', name_slug)])
                if len(brand) > 1:
                    raise Exception("More than one brand with the same slug_name %s" % name_slug)
                assert brand, (
                    "brand_name %s should have been imported in "
                    "product_template._import_dependencies" % (brand_name,))
                return {'product_brand_id': brand.id}

    @mapping
    def partner_stock_ids(self, record):
        values = {
            'status': record['AvailabilityCode'],
            'quantity': record['AvailableQuantity'],
            'last_update': fields.Datetime.now()
        }
        binding = self.options.get("binding")
        product_template = self.binder_for().unwrap_binding(binding)
        partner_stock = binding.partner_stock_ids.filtered(
            lambda x: x.partner_id == self.backend_record.partner_id and
                      x.product_tmpl_id.id == product_template.id
        )
        if partner_stock:
            partner_stock_ids = [(1, partner_stock.id, values)]
        else:
            values.update({
                'partner_id': self.backend_record.partner_id.id
            })
            partner_stock_ids = [(0, 0, values)]
        return {'partner_stock_ids': partner_stock_ids}

    @mapping
    def product_uom(self, record):
        product_uom_map = self.backend_record.get_product_uom_map(record['quantityUnitCode'])
        binding = self.options.get("binding")
        other_bindings = binding.veloconnect_bind_ids.filtered(
            lambda x: x.backend_id != self.backend_record and x.uom_po_id != product_uom_map)
        if other_bindings:
            raise ValidationError(_("Purchase Unit of Measure are different between backends. %s") % product_uom_map)
        return {
            'uom_po_id': product_uom_map.id,
            'uom_id': product_uom_map.id
        }

    # TODO: Mirar si les imatges existeixen abans d'importarles
    # implementar compatibilitat amb swipe_images_backend
    @mapping
    def image_1920(self, record):
        if record['InformationURLPicture']:
            url = record['InformationURLPicture']
            try:
                res = requests.get(url, params={'d': '404', 's': '128'}, timeout=5)
                if res.status_code != requests.codes.ok:
                    return False
            except requests.exceptions.ConnectionError as e:
                return False
            except requests.exceptions.Timeout as e:
                return False
            return {'image_1920': base64.b64encode(res.content)}
