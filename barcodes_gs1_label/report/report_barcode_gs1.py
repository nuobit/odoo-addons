# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from decimal import Decimal

import requests.utils

from odoo import _, api, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round


def chunks(li, n, padding=False):
    if not li:
        return
    sub_li = li[:n]
    if padding:
        diff = n - len(sub_li)
        if diff:
            sub_li += [None] * diff
    yield sub_li
    yield from chunks(li[n:], n, padding=padding)


class ReportGS1Barcode(models.AbstractModel):
    _name = "report.barcodes_gs1_label.report_gs1_barcode"
    _description = "Report GS1 Barcode"

    @property
    def FNC1(self):
        return {
            "gs1-128": "\xf1",
            "gs1-datamatrix": "\xe7",
        }

    @property
    def GS1_AI_FORMAT(self):
        return {
            "01": (14, False),
            "10": (20, True),
            "21": (20, True),
            "3100": (6, False),
            "3101": (6, False),
            "3102": (6, False),
            "3103": (6, False),
            "3104": (6, False),
            "3105": (6, False),
        }

    @api.model
    def _get_product_lot(self, products, quants, with_stock):
        docs = []
        if with_stock:
            prods = quants.product_id
        else:
            prods = products
        for product in prods:
            if product.tracking == "none":
                label = {"product": product, "lot": None}
                if with_stock:
                    for q in quants.filtered(
                        lambda x, prod=product: x.product_id == prod
                    ):
                        docs += [label] * int(q.quantity)
                else:
                    docs.append(label)
            elif product.tracking in ("lot", "serial"):
                if with_stock:
                    for q in quants.filtered(
                        lambda x, prod=product: x.product_id == prod
                    ).sorted(lambda x: x.lot_id.name or ""):
                        docs += [
                            {
                                "product": product,
                                "lot": q.lot_id,
                            }
                        ] * int(q.quantity)
                else:
                    lots = self.env["stock.lot"].search(
                        [("product_id", "=", product.id)]
                    )
                    for lot in lots.sorted(lambda x: x.name):
                        docs.append(
                            {
                                "product": product,
                                "lot": lot,
                            }
                        )
        return docs

    @api.model
    def _prepare_product_product_values(self, params):
        model, ids, with_stock, stock_location_ids, weight = (
            params["model"],
            params["ids"],
            params["with_stock"],
            params["stock_location_ids"],
            params["weight"],
        )

        docs = []
        for product in (
            self.env[model].browse(ids).sorted(lambda x: x.default_code or "")
        ):
            quants = self.env["stock.quant"]
            if with_stock:
                quants = self.env["stock.quant"].search(
                    [
                        ("product_id", "=", product.id),
                        ("location_id.usage", "=", "internal"),
                        ("location_id", "in", stock_location_ids),
                        ("quantity", ">", 0),
                        ("company_id", "=", self.env.company.id),
                    ]
                )
            for pd in self._get_product_lot(product, quants, with_stock):
                if weight > 0:
                    # the wizard asks the weight in kg, whatever the product's unit
                    pd.update(
                        {
                            "uom": self.env.ref("uom.product_uom_kgm"),
                            "qty": weight,
                        }
                    )
                docs.append(pd)
        return docs

    @api.model
    def _prepare_stock_lot_values(self, params):
        model, ids, with_stock, stock_location_ids, weight = (
            params["model"],
            params["ids"],
            params["with_stock"],
            params["stock_location_ids"],
            params["weight"],
        )
        docs = []
        for lot in (
            self.env[model]
            .browse(ids)
            .filtered(lambda x: x.product_id.tracking in ("lot", "serial"))
            .sorted(lambda x: x.product_id.default_code or "")
        ):
            quants = self.env["stock.quant"]
            if with_stock:
                quants = self.env["stock.quant"].search(
                    [
                        ("product_id", "=", lot.product_id.id),
                        ("location_id.usage", "=", "internal"),
                        ("location_id", "in", stock_location_ids),
                        ("lot_id", "=", lot.id),
                        ("quantity", ">", 0),
                        ("company_id", "=", self.env.company.id),
                    ]
                )
            values = {
                "product": lot.product_id,
                "lot": lot,
            }
            if weight > 0:
                # the wizard asks the weight in kg, whatever the product's unit
                values.update(
                    {
                        "uom": self.env.ref("uom.product_uom_kgm"),
                        "qty": weight,
                    }
                )
            if with_stock:
                for q in quants.sorted(lambda x: x.lot_id.name or ""):
                    docs += [values] * int(q.quantity)
            else:
                docs.append(values)
        return docs

    @api.model
    def _prepare_stock_quant_values(self, params):
        model, ids, with_stock = params["model"], params["ids"], params["with_stock"]
        docs = []
        for quant in (
            self.env[model]
            .browse(ids)
            .sorted(lambda x: x.product_id.default_code or "")
        ):
            quants = self.env["stock.quant"]
            if with_stock:
                quants = self.env["stock.quant"].search(
                    [
                        ("id", "=", quant.id),
                        ("location_id.usage", "=", "internal"),
                        ("location_id", "=", quant.location_id.id),
                        ("quantity", ">", 0),
                        ("company_id", "=", self.env.company.id),
                    ]
                )
            docs += self._get_product_lot(quant.product_id, quants, with_stock)
        return docs

    @api.model
    def _prepare_stock_picking_values(self, params):
        model, ids = params["model"], params["ids"]

        # sort by product and lot
        move_lines_tracking = {}
        for m in self.env[model].browse(ids).mapped("move_ids_without_package"):
            move_lines = m.move_line_ids.filtered(lambda x: x.state == "done")
            if not move_lines:
                raise UserError(_("There are no done move lines"))
            for ml in move_lines:
                key = (ml.product_id, ml.lot_id)
                move_lines_tracking.setdefault(key, []).append(ml)

        # prepare the final list of labels
        docs = []
        for _dummy, move_lines in dict(sorted(move_lines_tracking.items())).items():
            for ml in move_lines:
                if ml.quantity > 0:
                    expand_qty, uom, qty_per_doc = self._get_picking_line_labels(ml)
                    docs += [
                        {
                            "product": ml.product_id,
                            "lot": ml.lot_id or None,
                            "uom": uom,
                            "qty": qty_per_doc,
                        }
                    ] * expand_qty
        return docs

    @api.model
    def _get_picking_line_labels(self, ml):
        """Return how many labels a done line of a picking prints, and the
        unit and the quantity that each of them carries"""
        unit_uom = self.env.ref("uom.product_uom_categ_unit")
        weight_uom = self.env.ref("uom.product_uom_categ_kgm")
        # the unit of the products' weight field: kg, or lb when so configured
        product_weight_uom = self.env[
            "product.template"
        ]._get_weight_uom_id_from_ir_config_parameter()

        expand_qty = 1
        qty_per_doc = ml.quantity * ml.product_id.weight
        if ml.product_uom_category_id == unit_uom:
            expand_qty = ml.quantity
            qty_per_doc = ml.product_id.weight
        elif ml.product_uom_category_id == weight_uom:
            qty_per_doc = ml.quantity

        # a line in a weight unit carries its own quantity; any other
        # line carries the weight of its product
        uom = (
            ml.product_uom_id
            if ml.product_uom_category_id == weight_uom
            else product_weight_uom
        )
        return int(expand_qty), uom, qty_per_doc

    @api.model
    def _get_weight_text(self, weight):
        """A weight in fixed point: str() writes a small one as 1e-05"""
        return format(Decimal(repr(weight)), "f")

    @api.model
    def _get_weight_ai31(self, weight):
        max_ai31_length = 6
        max_ai31_decimals = 5
        # every digit of the weight, so that none is rounded away unseen
        weight_text = self._get_weight_text(weight)
        whole_str, _dot, decimal_str = weight_text.partition(".")
        whole_str = whole_str.lstrip("0")
        decimal_str = decimal_str.rstrip("0")
        if len(decimal_str) > max_ai31_decimals:
            raise UserError(
                _(
                    "The weight %(weight)s kg has more decimals than the 5 a GS1 "
                    "label holds. Correct it."
                )
                % {"weight": weight_text}
            )
        weight_flat_str = whole_str + decimal_str
        if len(weight_flat_str) > max_ai31_length:
            raise UserError(
                _(
                    "The weight %(weight)s kg has more digits than the 6 a GS1 label "
                    "holds, whole and decimal together. Correct it."
                )
                % {"weight": weight_text}
            )
        weight_ai = f"310{len(decimal_str)}"
        weight_value = f"{weight_flat_str}".rjust(max_ai31_length, "0")
        return weight_ai, weight_value

    @api.model
    def _prepare_gs1_values(self, data):
        product, lot = data["product"], data["lot"]
        if lot and lot.product_id != product:
            raise ValidationError(
                _(
                    "Incoherent data: the lot %(lot_name)s doesn't "
                    "belong to the product %(product_name)s. "
                    "Please report this issue to your administrator."
                )
                % {"lot_name": lot.name, "product_name": product.display_name}
            )
        res = {}
        if product.barcode:
            res["01"] = product.barcode.rjust(14, "0")
        if lot:
            if product.tracking == "lot":
                res["10"] = lot.name
            elif product.tracking == "serial":
                if lot.ref:
                    res["10"] = lot.ref
                res["21"] = lot.name

        weight = self._get_label_weight(data)
        if weight:
            weight_ai, weight_value = self._get_weight_ai31(weight)
            res[weight_ai] = weight_value
        return res

    @api.model
    def _get_label_weight(self, data):
        """The label's net weight in kg, 0 when it has none.

        GS1 writes the weight in kg: a weight in another unit is converted,
        then rounded to the five decimals the AI holds."""
        uom, qty = data.get("uom"), data.get("qty")
        kg = self.env.ref("uom.product_uom_kgm")
        if not uom or not qty or uom.category_id != kg.category_id:
            return 0
        if uom == kg:
            return qty
        return float_round(
            uom._compute_quantity(qty, kg, round=False), precision_digits=5
        )

    def _get_gs1_barcode_string(self, gs1_barcode, barcode_type):
        fnc1 = self.FNC1[barcode_type]
        res = [fnc1]
        gs1 = gs1_barcode.items()
        for i, (key, value) in enumerate(gs1, 1):
            if key not in self.GS1_AI_FORMAT:
                raise ValidationError(
                    _("The GS1 AI %s is not defined in GS1 AI format") % key
                )
            length, fnc1_required = self.GS1_AI_FORMAT[key]
            if len(value) > length:
                raise ValidationError(
                    _(
                        "The value '%(value)s' of GS1 AI %(key)s "
                        "is too long (max %(length)s characters)"
                    )
                    % {"value": value, "key": key, "length": length}
                )
            res.append(key + value)
            if fnc1_required and i < len(gs1):
                res.append(fnc1)
        return requests.utils.quote("".join(res))

    @api.model  # noqa: C901
    def _get_report_values(self, docids, data=None):  # noqa: C901
        # Odoo always adds the report type to the data; the label options come
        # only from the print wizard, which marks them
        if not data or "from_print_wizard" not in data:
            raise UserError(
                _(
                    "The labels are printed with the options of the print wizard: "
                    "open it from the records and choose the label options."
                )
            )

        # format params
        barcode_type = data["barcode_type"]
        show_price = data["show_price"]
        show_price_currency = data["show_price_currency"]

        cols = data["layout"]["cols"]
        start_cell = data["layout"]["start_cell"]
        labels_page_count = data["layout"]["labels_page_count"]
        label_copies = data["layout"]["label_copies"]

        # data params
        model = data["model"]
        data_params = {
            "model": model,
            "ids": data["ids"],
            "with_stock": data["with_stock"],
            "stock_location_ids": data["stock_location_ids"],
            "weight": data["weight"],
        }

        # generate product data
        func_name = f"_prepare_{model.replace('.', '_')}_values"
        func = getattr(self, func_name, None)
        if not func:
            raise UserError(
                _("The model '%(model)s' is not supported by this report.")
                % {"model": model}
            )
        docs1 = func(data_params)
        # a configuration that shows no weight prints its labels without one
        if not data["show_weight"]:
            docs1 = [
                {key: value for key, value in doc.items() if key not in ("uom", "qty")}
                for doc in docs1
            ]

        # generate label data
        docs = []
        for doc in docs1:
            product, lot = doc["product"], doc["lot"]
            if barcode_type in ("gs1-128", "gs1-datamatrix"):
                gs1_barcode = self._prepare_gs1_values(doc)
                if gs1_barcode:
                    barcode_string = self._get_gs1_barcode_string(
                        gs1_barcode, barcode_type
                    )
                    doc["barcode_values"] = gs1_barcode
                    doc["barcode_string"] = barcode_string
                else:
                    doc["barcode_values"] = None
                    doc["barcode_string"] = None
            elif barcode_type == "ean13-code128":
                doc["barcode_values"] = (
                    product.barcode or None,
                    product.tracking != "none" and lot and lot.name or None,
                )
            elif barcode_type == "ean13":
                doc["barcode_values"] = product.barcode or None
            else:
                raise ValidationError(_("Unknown barcode type %s") % barcode_type)

            if product.tracking in ("none", "lot") and label_copies > 1:
                docs += [doc] * label_copies
            else:
                docs.append(doc)

        # format and print labels
        docs_padded = [None] * (start_cell - 1) + docs
        docs_paginated = chunks(docs_padded, labels_page_count)
        docs_page_rows = [list(chunks(x, cols, padding=True)) for x in docs_paginated]

        return {
            "docs": docs_page_rows,
            "show_price": show_price,
            "show_price_currency": show_price_currency,
            "barcode_type": barcode_type,
            "layout": data["layout"],
        }
