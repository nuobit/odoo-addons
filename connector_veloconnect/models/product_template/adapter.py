# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import datetime
import itertools

from odoo import _
import pyveloedi.veloconnect as vc
from odoo.addons.component.core import Component
from odoo.exceptions import ValidationError
from odoo.addons.connector_veloconnect.models.common import tools
from odoo.addons.queue_job.exception import RetryableJobError


def base_prices(elements):
    ct = [
        ('cbc:PriceAmount', lambda x: float(x.text or 0), 'PriceAmount', False),
        ('cbc:PriceAmount', lambda x: x.attrib['amountCurrencyID'], 'amountCurrencyID', False),
        ('cbc:BaseQuantity', lambda x: int(x.text or 0), 'BaseQuantity', False),
        ('cbc:BaseQuantity', lambda x: x.attrib['quantityUnitCode'], 'quantityUnitCode', False),
        ('cbc:MinimumQuantity', lambda x: int(x.text or 0), 'MinimumQuantity', False),
        ('cbc:MinimumQuantity', lambda x: x.attrib['quantityUnitCode'], 'MinimumQuantityUnitCode', False),
    ]
    return tools.convert_to_json(elements, ct, namespace=vc.NAMESPACES)


ct = [
    ('cac:Item/cac:SellersItemIdentification/cac:ID', lambda x: x.text or None, 'SellersItemIdentificationID', False),
    ('cac:Item/vco:RequestReplacement/cac:ItemReplacement/cac:ID', lambda x: x.text or None, 'RequestReplacementID',
     False),
    ('cac:Item/cbc:Description', lambda x: x.text or None, 'Description', False),
    # ('cac:Item/cbc:Description', lambda x: str(x).replace(r'&nbsp;',' '), 'description'),
    ('cac:Item/cac:RecommendedRetailPrice/cbc:PriceAmount', lambda x: float(x.text or 0), 'RecommendedRetailPrice',
     False),

    ('cac:Item/cac:BasePrice', base_prices, 'BasePrice', True),

    ('cac:Item/cac:ManufacturersItemIdentification/cac:IssuerParty/cac:PartyName/cbc:Name', lambda x: x.text or None,
     'ManufacturersItemIdentificationName', False),
    ('cac:Item/cac:ManufacturersItemIdentification/cac:ID', lambda x: x.text or None,
     'ManufacturersItemIdentificationID',
     False),
    ('vco:Availability/vco:Code', lambda x: x.text or None, 'AvailabilityCode', False),
    ('vco:Availability/vco:AvailableQuantity', lambda x: int(x.text or 0), 'AvailableQuantity', False),
    ('cac:Item/cac:StandardItemIdentification/cac:ID[@identificationSchemeID="EAN/UCC-13"]', lambda x: x.text or None,
     'StandardItemIdentification', False),
    ('cac:Item/vcc:ItemInformation/vcc:InformationURL/vcc:Disposition[text()="picture"]/../vcc:URI',
     lambda x: x.text or None,
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

    def search_read(self, domain, offset, chunk_size):

        filters_values = ["Hash"]
        real_domain, common_domain = self._extract_domain_clauses(
            domain, filters_values
        )
        res = []
        context = vc.Context(url=self.backend_record.url, userid=self.backend_record.buyer,
                             passwd=self.backend_record.password, istest=True, log=False,
                             use_objects=False)
        context._load_params()
        while chunk_size:
            cts = vc.CreateTextSearch(context)
            try:
                ctsresp = cts.execute('')
            except vc.VeloConnectException as e:
                if e.code == 420 or e.code == 421:
                    raise RetryableJobError(_("%s. The job will be retried later") % e.message,
                                            seconds=self.backend_record.product_search_retry_time * 60)
                raise
            sr = vc.SearchReadResult(context)
            items = sr.execute(ctsresp.tan, offset, chunk_size)
            res += items
            len_items = len(items)
            chunk_size -= len_items
            if chunk_size < 0:
                raise ValidationError(_("Unexpected Error: Chunk_size is < 0"))
            offset += len_items
        res = tools.convert_to_json(res, ct, vc.NAMESPACES)
        res = self._reorg_product_data(res)
        res = self._filter(res, common_domain)
        res = self._filter_by_hash(res)
        return res

    # TODO: Duplicated code, refactor
    def get_total_items(self):
        context = vc.Context(url=self.backend_record.url, userid=self.backend_record.buyer,
                             passwd=self.backend_record.password, istest=True, log=False,
                             use_objects=False)
        context._load_params()
        cts = vc.CreateTextSearch(context)
        return cts.execute('').count

    def _reorg_product_data(self, values):
        # reorganize data
        hash_fields = ['SellersItemIdentificationID', 'RequestReplacementID', 'Description', 'RecommendedRetailPrice',
                       'ManufacturersItemIdentificationName', 'ManufacturersItemIdentificationID', 'AvailabilityCode',
                       'AvailableQuantity', 'StandardItemIdentification', 'quantityUnitCode',
                       'InformationURLPicture']
        base_price_fields = ['PriceAmount', 'amountCurrencyID', 'BaseQuantity', 'MinimumQuantity',
                             'MinimumQuantityUnitCode']
        for value in values:
            min_qties = {}
            price_hash = []
            product_uom = None
            for price in value['BasePrice']:
                if product_uom is None:
                    product_uom = price['quantityUnitCode']
                elif product_uom != price['quantityUnitCode']:
                    raise ValidationError(_("Product with different UOMs"))

                price_hash.append(tools.list2hash([price[x] or None for x in base_price_fields]))
                min_qties.setdefault(price['MinimumQuantity'] or 0, []).append({
                    'SellersItemIdentificationID': value['SellersItemIdentificationID'],
                    'PriceAmount': price['PriceAmount'],
                    'amountCurrencyID': price['amountCurrencyID'],
                    'BaseQuantity': price['BaseQuantity'],
                    'MinimumQuantity': price['MinimumQuantity'] or 0,
                    'MinimumQuantityUnitCode': price['MinimumQuantityUnitCode'],
                })
                product_uom_mapped = self.backend_record.get_product_uom_map(product_uom)

                price['Hash_supplierinfo'] = tools.list2hash(
                    [tools.list2hash([price['PriceAmount']])] +
                    [tools.list2hash([value['SellersItemIdentificationID']])] +
                    [tools.list2hash([price['MinimumQuantity'] or 0])] +
                    [tools.list2hash([value['StandardItemIdentification']])] +
                    [tools.list2hash([product_uom_mapped.id])]
                )

            # The code below prevents multiple BasePrice with the same MinimumQuantity.
            # It check if the price is consistent and if we find more than one match (or none) we throw an error.
            found = None
            sorted_prices = [y[1] for y in sorted(min_qties.items(), key=lambda x: x[0])]
            for price in itertools.product(*sorted_prices):
                t = [x['PriceAmount'] for x in price]
                diffs = [i - j for i, j in zip(t[:-1], t[1:])]
                positives = all(map(lambda x: x >= 0, diffs))
                if positives:
                    if found is not None:
                        raise ValidationError(_("More than one BasePrice consistent found"))
                    found = price
            if not found:
                raise ValidationError(_("BasePrice is no consistent"))
            value['items'] = found
            value['quantityUnitCode'] = product_uom
            value['Hash'] = tools.list2hash([value[x] or None for x in hash_fields] + [tools.list2hash(price_hash)])
        return values
