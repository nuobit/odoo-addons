# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


import pyveloedi.veloconnect as vc

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.queue_job.exception import RetryableJobError

from ..common import tools


def base_prices(elements):
    XML_TO_JSON_MAP = [
        ("cbc:PriceAmount", lambda x: float(x.text or 0), "PriceAmount", False),
        (
            "cbc:PriceAmount",
            lambda x: x.attrib["amountCurrencyID"],
            "amountCurrencyID",
            False,
        ),
        ("cbc:BaseQuantity", lambda x: int(x.text or 0), "BaseQuantity", False),
        (
            "cbc:BaseQuantity",
            lambda x: x.attrib["quantityUnitCode"],
            "quantityUnitCode",
            False,
        ),
        ("cbc:MinimumQuantity", lambda x: int(x.text or 0), "MinimumQuantity", False),
        (
            "cbc:MinimumQuantity",
            lambda x: x.attrib["quantityUnitCode"],
            "MinimumQuantityUnitCode",
            False,
        ),
    ]
    return tools.convert_to_json(elements, XML_TO_JSON_MAP, namespace=vc.NAMESPACES)


XML_TO_JSON_MAP = [
    (
        "cac:Item/cac:SellersItemIdentification/cac:ID",
        lambda x: x.text or None,
        "SellersItemIdentificationID",
        False,
    ),
    (
        "cac:Item/vco:RequestReplacement/cac:ItemReplacement/cac:ID",
        lambda x: x.text or None,
        "RequestReplacementID",
        False,
    ),
    ("cac:Item/cbc:Description", lambda x: x.text or None, "Description", False),
    # ('cac:Item/cbc:Description', lambda x: str(x).replace(r'&nbsp;',' '), 'description'),
    (
        "cac:Item/cac:RecommendedRetailPrice/cbc:PriceAmount",
        lambda x: float(x.text or 0),
        "RecommendedRetailPrice",
        False,
    ),
    ("cac:Item/cac:BasePrice", base_prices, "BasePrice", True),
    (
        "cac:Item/cac:ManufacturersItemIdentification/cac:IssuerParty/cac:PartyName/cbc:Name",
        lambda x: x.text or None,
        "ManufacturersItemIdentificationName",
        False,
    ),
    (
        "cac:Item/cac:ManufacturersItemIdentification/cac:ID",
        lambda x: x.text or None,
        "ManufacturersItemIdentificationID",
        False,
    ),
    ("vco:Availability/vco:Code", lambda x: x.text or None, "AvailabilityCode", False),
    (
        "vco:Availability/vco:AvailableQuantity",
        lambda x: int(x.text or 0),
        "AvailableQuantity",
        False,
    ),
    (
        'cac:Item/cac:StandardItemIdentification/cac:ID[@identificationSchemeID="EAN/UCC-13"]',
        lambda x: x.text or None,
        "StandardItemIdentification",
        False,
    ),
    (
        "cac:Item/vcc:ItemInformation/vcc:InformationURL"
        '/vcc:Disposition[text()="picture"]/../vcc:URI',
        lambda x: x.text or None,
        "InformationURLPicture",
        False,
    ),
]
PRODUCT_HASH_FIELDS = [
    "SellersItemIdentificationID",
    "RequestReplacementID",
    "Description",
    "RecommendedRetailPrice",
    "ManufacturersItemIdentificationName",
    "ManufacturersItemIdentificationID",
    "AvailabilityCode",
    "AvailableQuantity",
    "StandardItemIdentification",
    "quantityUnitCode",
    "InformationURLPicture",
]
BASE_PRICE_HASH_FIELDS = [
    "PriceAmount",
    "amountCurrencyID",
    "BaseQuantity",
    "MinimumQuantity",
    "MinimumQuantityUnitCode",
]


class VeloconnectProductTemplateAdapter(Component):
    _name = "veloconnect.product.template.adapter"
    _inherit = "veloconnect.adapter"

    _apply_on = "veloconnect.product.template"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vc_context = vc.Context(
            url=self.backend_record.url,
            userid=self.backend_record.buyer,
            passwd=self.backend_record.password,
            istest=False,
            log=False,
            use_objects=False,
        )
        self.vc_context._load_params()

    def _prepare_results(self, result):
        return result

    # pylint: disable=W8106
    def read(self, code):
        # we cannot use getItemDetals because Specialized does not implement it right
        gid = vc.GetItemDetailsList(self.vc_context)
        items = gid.execute([code])
        res = tools.convert_to_json(items, XML_TO_JSON_MAP, vc.NAMESPACES)
        self._reorg_product_data(res)
        if not res:
            return None
        return res[0]

    def search_read(self, domain, offset, chunk_size):
        ctsresp = self._get_text_search_transaction()
        sr = vc.SearchReadResult(self.vc_context)
        items = sr.execute(ctsresp.tan, offset, chunk_size)
        len_items = len(items)
        res = tools.convert_to_json(items, XML_TO_JSON_MAP, vc.NAMESPACES)
        self._reorg_product_data(res)
        res = self._filter(res, domain)
        res = self._filter_by_hash(res)
        return res, len_items

    def get_total_items(self):
        return self._get_text_search_transaction().count

    def _get_text_search_transaction(self):
        cts = vc.CreateTextSearch(self.vc_context)
        try:
            ctsresp = cts.execute("")
        except vc.VeloConnectException as e:
            if e.code in (420, 421, 514):
                raise RetryableJobError(
                    _("%s. The job will be retried later") % str(e),
                    seconds=self.backend_record.product_search_retry_time * 60,
                )
            raise
        return ctsresp

    def _reorg_product_item(self, value):
        price_hash = []
        product_uom = None
        for price in value["BasePrice"]:
            if product_uom is None:
                product_uom = price["quantityUnitCode"]
            elif product_uom != price["quantityUnitCode"]:
                raise ValidationError(_("Product with different UOMs"))
            price_hash.append(
                tools.list2hash([price[x] or None for x in BASE_PRICE_HASH_FIELDS])
            )
            value.setdefault("items", []).append(
                {
                    "SellersItemIdentificationID": value["SellersItemIdentificationID"],
                    "PriceAmount": price["PriceAmount"],
                    "amountCurrencyID": price["amountCurrencyID"],
                    "BaseQuantity": price["BaseQuantity"],
                    "MinimumQuantity": price["MinimumQuantity"] or 0,
                    "MinimumQuantityUnitCode": price["MinimumQuantityUnitCode"],
                }
            )
        value["quantityUnitCode"] = product_uom
        value["Hash"] = tools.list2hash(
            [value[x] or None for x in PRODUCT_HASH_FIELDS]
            + [tools.list2hash(price_hash)]
        )

    def _reorg_product_data(self, values):
        # reorganize data
        for value in values:
            self._reorg_product_item(value)
