# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import datetime

from odoo import _
import pyveloedi.veloconnect as vc
from odoo.addons.component.core import Component
from odoo.exceptions import ValidationError
from odoo.addons.connector_veloconnect.models.common import tools


# new camp multi

def base_prices(elements):
    ct = [
        ('cbc:PriceAmount', lambda x: float(x.text), 'PriceAmount', False),
        ('cbc:PriceAmount', lambda x: x.attrib['amountCurrencyID'], 'amountCurrencyID', False),
        ('cbc:BaseQuantity', lambda x: int(x.text), 'BaseQuantity', False),
        ('cbc:BaseQuantity', lambda x: x.attrib['quantityUnitCode'], 'quantityUnitCode', False),
        ('cbc:MinimumQuantity', lambda x: int(x.text), 'MinimumQuantity', False),
        ('cbc:MinimumQuantity', lambda x: x.attrib['quantityUnitCode'], 'MinimumQuantityUnitCode', False),
    ]
    return tools.convert_to_json(elements, ct, namespace=vc.NAMESPACES)


ct = [
    ('cac:Item/cac:SellersItemIdentification/cac:ID', lambda x: x.text, 'SellersItemIdentificationID', False),
    ('cac:Item/vco:RequestReplacement/cac:ItemReplacement/cac:ID', lambda x: x.text, 'RequestReplacementID', False),
    ('cac:Item/cbc:Description', lambda x: x.text, 'Description', False),
    # ('cac:Item/cbc:Description', lambda x: str(x).replace(r'&nbsp;',' '), 'description'),
    ('cac:Item/cac:RecommendedRetailPrice/cbc:PriceAmount', lambda x: float(x.text), 'RecommendedRetailPrice', False),

    ('cac:Item/cac:BasePrice', base_prices, 'BasePrice', True),

    ('cac:Item/cac:ManufacturersItemIdentification/cac:IssuerParty/cac:PartyName/cbc:Name', lambda x: x.text,
     'ManufacturersItemIdentificationName', False),
    ('cac:Item/cac:ManufacturersItemIdentification/cac:ID', lambda x: x.text, 'ManufacturersItemIdentificationID',
     False),
    ('vco:Availability/vco:Code', lambda x: x.text, 'AvailabilityCode', False),
    ('vco:Availability/vco:AvailableQuantity', lambda x: int(x.text), 'AvailableQuantity', False),
    ('cac:Item/cac:StandardItemIdentification/cac:ID[@identificationSchemeID="EAN/UCC-13"]', lambda x: x.text,
     'StandardItemIdentification',
     False),
    ('cac:Item/vcc:ItemInformation/vcc:InformationURL/vcc:Disposition[text()="picture"]/../vcc:URI', lambda x: x.text,
     'InformationURLPicture', False),
]


class VeloconnectProductTemplateTypeAdapter(Component):
    _name = "veloconnect.product.template.adapter"
    _inherit = "veloconnect.adapter"

    _apply_on = "veloconnect.product.template"

    def _prepare_results(self, result):
        return result

    def read(self, _id):
        external_id_values = self.binder_for().id2dict(_id, in_field=False)
        domain = [(key, "=", value) for key, value in external_id_values.items()]
        res = self.search_read(domain)
        if len(res) > 1:
            raise ValidationError(_("Found more than 1 record for an unique key %s") % _id)
        return res[0] or None

    def search_read(self, domain, limit, offset):
        filters_values = ["Hash"]
        real_domain, common_domain = self._extract_domain_clauses(
            domain, filters_values
        )

        context = vc.Context(url=self.backend_record.veloconnect_url, userid=self.backend_record.veloconnect_user,
                             passwd=self.backend_record.veloconnect_password, istest=True, log=False, use_objects=False)
        context._load_bindings()

        cts = vc.CreateTextSearch(context)
        # to_delete?
        # ctsresp = cts.execute('')
        ctsresp = cts.execute('')
        # ctsresp = cts.execute('26.01')

        total_count = ctsresp.count
        if total_count == 0:
            return [], 0, 0

        sr = vc.SearchReadResult(context)
        if limit <= 0:
            limit = ctsresp.count

        items = sr.execute(ctsresp.tan, offset, limit)

        res = tools.convert_to_json(items, ct, vc.NAMESPACES)
        len_items = len(res)
        left_items = total_count - offset - len_items
        res = self._reorg_product_data(res)
        res = self._filter(res, common_domain)
        return res, len_items, left_items

        # to_do: poner filtros bien
        # filters_values = ["Description", "SellersItemIdentification"]
        # real_domain, common_domain = self._extract_domain_clauses(
        #     domain, filters_values
        # )
        # real_domain = self._convert_format_domain(real_domain)
        # # kw_base_params = self.domain_to_normalized_dict(real_domain)
        # # TODO: treure fora de la funció
        # context = vc.VeloContext(url=self.backend_record.veloconnect_url, userid=self.backend_record.veloconnect_user,
        #                          passwd=self.backend_record.veloconnect_password, istest=True, log=True)
        # res = context.get("Product").search_read('', offset=offset, limit=limit, count=False)
        # # TODO: utilitzar ID_ONLY + filter per evitar que retorni mes resultats del compte
        #
        # # self._format_order_data(res)
        # # res = self._filter(res, common_domain)
        # # self._reorg_order_data(res)
        # return res

    def _reorg_product_data(self, values):
        # reorganize data
        hash_fields = ['SellersItemIdentificationID', 'RequestReplacementID', 'Description', 'RecommendedRetailPrice',
                       'ManufacturersItemIdentificationName', 'ManufacturersItemIdentificationID', 'AvailabilityCode',
                       'AvailableQuantity', 'StandardItemIdentification',
                       'InformationURLPicture']
        base_price_fields = ['PriceAmount', 'amountCurrencyID', 'BaseQuantity', 'quantityUnitCode', 'MinimumQuantity',
                             'MinimumQuantityUnitCode']
        price_hash = []

        for value in values:
            value['items'] = []
            for price in value['BasePrice']:
                price_hash.append(tools.list2hash([price[x] or None for x in base_price_fields]))
                value['items'].append({
                    'SellersItemIdentificationID': value['SellersItemIdentificationID'],
                    'PriceAmount': price['PriceAmount'],
                    'amountCurrencyID': price['amountCurrencyID'],
                    'BaseQuantity': price['BaseQuantity'],
                    'quantityUnitCode': price['quantityUnitCode'],
                    'MinimumQuantity': price['MinimumQuantity'] or 0,
                    'MinimumQuantityUnitCode': price['MinimumQuantityUnitCode'],
                })
            value['Hash'] = tools.list2hash([value[x] or None for x in hash_fields] + [tools.list2hash(price_hash)])
        return values
