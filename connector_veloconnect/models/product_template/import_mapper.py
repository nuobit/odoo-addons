# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, only_create)
from odoo.addons.connector_veloconnect.models.common import tools


class ProductTemplateImportMapChild(Component):
    _name = 'veloconnect.product.template.map.child.import'
    _inherit = 'veloconnect.map.child.import'

    _apply_on = 'veloconnect.product.supplierinfo'

    def get_item_values(self, map_record, to_attr, options):
        binder = self.binder_for('veloconnect.product.supplierinfo')
        external_id = binder.dict2id(map_record.source, in_field=False)
        binding = binder.to_internal(external_id, unwrap=False)
        if binding:
            map_record.update(id=binding.id)
        return map_record.values(**options)

    def format_items(self, items_values):
        ops = []
        for values in items_values:
            id = values.pop('id', None)
            if id:
                ops.append((1, id, values))
            else:
                ops.append((0, False, values))
        return ops


class VeloconnectProductTemplateImportMapper(Component):
    _name = 'veloconnect.product.template.import.mapper'
    _inherit = 'veloconnect.import.mapper'

    _apply_on = 'veloconnect.product.template'

    direct = []

    children = [('items', 'veloconnect_seller_ids', 'veloconnect.product.supplierinfo')]

    # @mapping
    # def backend_id(self, record):
    #     return {'backend_id': self.backend_record.id}

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
    def binding_price(self, record):
        return {'veloconnect_price': record['RecommendedRetailPrice']}

    @mapping
    def default_code(self, record):
        manufacturer_id = record.get('ManufacturersItemIdentificationID')
        if manufacturer_id:
            binding = self.options.get("binding")
            if not binding or not binding.default_code:
                return {'default_code': manufacturer_id}

    @mapping
    def hash(self, record):
        hash_fields = ['SellersItemIdentificationID', 'RequestReplacementID', 'Description', 'RecommendedRetailPrice',
                       'ManufacturersItemIdentificationName', 'ManufacturersItemIdentificationID', 'AvailabilityCode',
                       'AvailableQuantity', 'StandardItemIdentification',
                       'InformationURLPicture']
        base_price_fields = ['PriceAmount', 'amountCurrencyID', 'BaseQuantity', 'quantityUnitCode', 'MinimumQuantity',
                             'MinimumQuantityUnitCode']
        price_hash = []
        for price in record['BasePrice']:
            price_hash.append(tools.list2hash([price[x] or None for x in base_price_fields]))
        return {'veloconnect_hash': tools.list2hash(
            [record[x] or None for x in hash_fields] + [tools.list2hash(price_hash)])}

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
