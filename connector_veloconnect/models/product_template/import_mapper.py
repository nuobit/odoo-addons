# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import base64

import requests
import urllib3

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from odoo.addons.queue_job.exception import RetryableJobError

from ..common import tools


class ProductTemplateImportMapChild(Component):
    _name = "veloconnect.product.template.map.child.import"
    _inherit = "veloconnect.map.child.import"

    _apply_on = "product.supplierinfo"

    def _prepare_existing_records(self, records):
        return records.filtered(lambda x: self.backend_record.partner_id == x.name)


class VeloconnectProductTemplateImportMapper(Component):
    _name = "veloconnect.product.template.import.mapper"
    _inherit = "veloconnect.import.mapper"

    _apply_on = "veloconnect.product.template"

    children = [("items", "seller_ids", "product.supplierinfo")]

    @mapping
    def barcode(self, record):
        backend_barcode = record["StandardItemIdentification"].strip()
        binding = self.options.get("binding")
        if not binding.barcode:
            return {"barcode": backend_barcode}
        else:
            if binding.barcode != backend_barcode:
                raise ValidationError(
                    _(
                        "Barcode has changed in backend since "
                        "last synchronization: %s (old) vs %s (new)"
                    )
                    % (binding.barcode, backend_barcode)
                )

    @only_create
    @mapping
    def name(self, record):
        if record["Description"] is None:
            return None
        return {"name": record["Description"]}

    @mapping
    def price(self, record):
        if record["RecommendedRetailPrice"]:
            binding = self.options.get("binding")
            other_bindings = binding.veloconnect_bind_ids.filtered(
                lambda x: x.backend_id != self.backend_record
            )
            max_price = max(
                [x.veloconnect_price for x in other_bindings]
                + [record["RecommendedRetailPrice"]]
            )
            if max_price:
                return {"list_price": max_price}

    @mapping
    def binding_description(self, record):
        return {"veloconnect_description": record["Description"]}

    @mapping
    def binding_price(self, record):
        return {"veloconnect_price": record["RecommendedRetailPrice"]}

    @mapping
    def binding_uom(self, record):
        return {"veloconnect_uom": record["quantityUnitCode"]}

    def _check_default_code(self, default_code, manufacturer_id):
        if default_code != manufacturer_id:
            raise ValidationError(
                _(
                    "The current internal reference %s is different "
                    "than the one is trying to import %s "
                )
                % (default_code, manufacturer_id)
            )

    @mapping
    def default_code(self, record):
        binding = self.options.get("binding")
        if (
            self.backend_record.is_manufacturer
            and record["SellersItemIdentificationID"]
        ):
            if not binding or not binding.veloconnect_bind_ids.filtered(
                lambda x: self.backend_record != x.backend_id and x.is_manufacturer
            ):
                return {"default_code": record["SellersItemIdentificationID"]}
        else:
            manufacturer_id = record.get("ManufacturersItemIdentificationID")
            if manufacturer_id:
                if not binding or not binding.default_code:
                    return {"default_code": manufacturer_id}
                self._check_default_code(binding.default_code, manufacturer_id)

    @mapping
    def hash(self, record):
        return {"veloconnect_hash": record["Hash"]}

    @mapping
    def product_brand_id(self, record):
        brand_name = record.get("ManufacturersItemIdentificationName")
        if brand_name:
            binding = self.options.get("binding")
            if not binding or not binding.product_brand_id:
                name_slug = tools.slugify(brand_name)
                brand = self.env["product.brand"].search(
                    [("name_slug", "=", name_slug)]
                )
                if len(brand) > 1:
                    raise Exception(
                        "More than one brand with the same slug_name %s" % name_slug
                    )
                assert brand, (
                    "brand_name %s should have been imported in "
                    "product_template._import_dependencies" % (brand_name,)
                )
                return {"product_brand_id": brand.id}

    @mapping
    def partner_stock_ids(self, record):
        values = {
            "status": record["AvailabilityCode"],
            "quantity": record["AvailableQuantity"],
            "sync_date": self.options["sync_date"],
        }
        binding = self.options.get("binding")
        product_template = self.binder_for().unwrap_binding(binding)
        partner_stock = binding.partner_stock_ids.filtered(
            lambda x: x.partner_id == self.backend_record.partner_id
            and x.product_tmpl_id.id == product_template.id
        )
        if self.backend_record.ignore_availablequantity:
            values.update(
                {
                    "quantity": -1,
                }
            )
        if partner_stock:
            partner_stock_ids = [(1, partner_stock.id, values)]
        else:
            values.update({"partner_id": self.backend_record.partner_id.id})
            partner_stock_ids = [(0, 0, values)]
        return {"partner_stock_ids": partner_stock_ids}

    @mapping
    def product_uom(self, record):
        unitcode = record["quantityUnitCode"]
        product_uom_map = self.backend_record.get_product_uom_map(
            record["quantityUnitCode"]
        )
        values = {"uom_po_id": product_uom_map.id}
        binding = self.options.get("binding")
        if not binding:
            values.update({"uom_id": product_uom_map.id})
        else:
            other_bindings = binding.veloconnect_bind_ids.filtered(
                lambda x: x.backend_id != self.backend_record
                and x.veloconnect_uom != unitcode
                and not x.backend_id.ignore_uom
            )
            if other_bindings and not self.backend_record.ignore_uom:
                raise ValidationError(
                    _(
                        "Purchase Unit of Measure are different between backends: %s vs %s"
                    )
                    % (unitcode, ", ".join(other_bindings.mapped("veloconnect_uom")))
                )
        return values

    # TODO: check if images exist before import
    @mapping
    def image_1920(self, record):
        if record["InformationURLPicture"]:
            url = record["InformationURLPicture"]
            try:
                res = requests.get(url)
                if res.status_code == requests.codes.ok:
                    return {"image_1920": base64.b64encode(res.content)}
                else:
                    return {"image_1920": None}
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                urllib3.exceptions.ProtocolError,
            ) as e:
                return RetryableJobError(
                    _("Connection Error getting picture from %s. %s") % (url, e)
                )
