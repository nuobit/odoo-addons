# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import requests.utils

from odoo import _, api, models
from odoo.exceptions import UserError, ValidationError


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
        for doc in self.env[model].browse(ids).sorted(lambda x: x.default_code or ""):
            quants = self.env["stock.quant"]
            if with_stock:
                quants = self.env["stock.quant"].search(
                    [
                        ("product_id", "=", doc.id),
                        ("location_id.usage", "=", "internal"),
                        ("location_id", "in", stock_location_ids),
                        ("quantity", ">", 0),
                        ("company_id", "=", self.env.company.id),
                    ]
                )
            docs += [
                {
                    **x,
                    "weight": weight,
                }
                for x in self._get_product_lot(doc, quants, with_stock)
            ]
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
        for doc in (
            self.env[model]
            .browse(ids)
            .filtered(lambda x: x.product_id.tracking in ("lot", "serial"))
            .sorted(lambda x: x.product_id.default_code or "")
        ):
            quants = self.env["stock.quant"]
            if with_stock:
                quants = self.env["stock.quant"].search(
                    [
                        ("product_id", "=", doc.product_id.id),
                        ("location_id.usage", "=", "internal"),
                        ("location_id", "in", stock_location_ids),
                        ("lot_id", "=", doc.id),
                        ("quantity", ">", 0),
                        ("company_id", "=", self.env.company.id),
                    ]
                )
            if with_stock:
                for q in quants.sorted(lambda x: x.lot_id.name or ""):
                    docs += [
                        {
                            "product": doc.product_id,
                            "lot": doc,
                            "weight": weight,
                        }
                    ] * int(q.quantity)
            else:
                docs.append(
                    {
                        "product": doc.product_id,
                        "lot": doc,
                        "weight": weight,
                    }
                )
        return docs

    @api.model
    def _prepare_stock_quant_values(self, params):
        model, ids, with_stock = params["model"], params["ids"], params["with_stock"]
        docs = []
        for doc in (
            self.env[model]
            .browse(ids)
            .sorted(lambda x: x.product_id.default_code or "")
        ):
            quants = self.env["stock.quant"]
            if with_stock:
                quants = self.env["stock.quant"].search(
                    [
                        ("id", "=", doc.id),
                        ("location_id.usage", "=", "internal"),
                        ("location_id", "=", doc.location_id.id),
                        ("quantity", ">", 0),
                        ("company_id", "=", self.env.company.id),
                    ]
                )
            docs += self._get_product_lot(doc.product_id, quants, with_stock)
        return docs

    # flake8: noqa: C901
    @api.model
    def _prepare_stock_picking_values(self, params):
        model, ids = params["model"], params["ids"]
        unit_uom = self.env.ref("uom.product_uom_categ_unit")
        weight_uom = self.env.ref("uom.product_uom_categ_kgm")

        # Add po qty proportional to each move line
        uom_po_moves = []
        for m in self.env[model].browse(ids).mapped("move_ids_without_package"):
            # compute the ratio of the uom of the PO (if exists)
            uom_po, uom_po_ratio = self.env["uom.uom"], 1
            if m.purchase_line_id:
                uom_po = m.purchase_line_id.product_uom
                if uom_po.dynamic_ratio:
                    all_move_lines = (
                        self.env["stock.move"]
                        .search(
                            [
                                ("picking_id", "=", m.picking_id.id),
                                ("purchase_line_id", "=", m.purchase_line_id.id),
                                ("state", "=", "done"),
                            ]
                        )
                        .move_line_ids
                    )
                    if len(all_move_lines.product_uom_id) != 1:
                        raise UserError(
                            _(
                                "All the lines must have the same UoM category "
                                "in a picking to print labels. "
                                "The line with the product: %(product)s has "
                                "multiple lots with different units of measure"
                            )
                            % {"product": m.product_id.display_name}
                        )
                    total_po_moves_qty = sum(all_move_lines.mapped("quantity"))
                    uom_po_qty = m.purchase_line_id.product_uom_qty
                    if uom_po_qty > 0:
                        uom_po_ratio = total_po_moves_qty / uom_po_qty
                else:
                    uom_po_ratio = uom_po.ratio

            values = {"move": m, "move_lines": []}
            move_lines = m.move_line_ids.filtered(lambda x: x.state == "done")
            if not move_lines:
                raise UserError(_("There are no done move lines"))
            for ml in move_lines:
                values["move_lines"].append(
                    {
                        "line": ml,
                        "uom_po": uom_po,
                        "uom_po_ratio": uom_po and uom_po_ratio or None,
                    }
                )
            uom_po_moves.append(values)

        # sort by product and lot
        move_lines_tracking = {}
        for m_d in uom_po_moves:
            for ml_d in m_d["move_lines"]:
                ml = ml_d["line"]
                key = (ml.product_id, ml.lot_id)
                move_lines_tracking.setdefault(key, []).append(ml_d)

        # prepare the final list of labels
        docs = []
        for _dummy, mov_lines_meta in dict(sorted(move_lines_tracking.items())).items():
            for ml_meta in mov_lines_meta:
                ml = ml_meta["line"]
                if ml.quantity > 0:
                    expand_qty = 1
                    weight_per_doc = ml.quantity * ml.product_id.weight
                    # compute po uom qty prorated for rhe current move line
                    if ml_meta["uom_po"].dynamic_ratio:
                        uom_po_ratio = ml_meta["uom_po_ratio"]
                        if ml.quantity % uom_po_ratio:
                            raise UserError(
                                _(
                                    "The quantity of the product %(product)s"
                                    " in the picking line is not a multiple "
                                    "of the weight unit of measure %(uom_ratio)s. "
                                    "Please correct it."
                                )
                                % {
                                    "product": ml.product_id.display_name,
                                    "uom_ratio": uom_po_ratio,
                                }
                            )
                        uom_po_qty = ml.quantity / uom_po_ratio
                        expand_qty = uom_po_qty
                        if ml.product_uom_category_id == weight_uom:
                            weight_per_doc = uom_po_ratio
                    else:
                        if ml.product_uom_category_id == unit_uom:
                            expand_qty = ml.quantity
                            weight_per_doc = ml.product_id.weight
                        elif ml.product_uom_category_id == weight_uom:
                            weight_per_doc = ml.quantity

                    docs += [
                        {
                            "product": ml.product_id,
                            "lot": ml.lot_id or None,
                            "weight": weight_per_doc,
                        }
                    ] * int(expand_qty)
        return docs

    @api.model
    def _get_weight_ai31(self, weight):
        max_ai31_length = 6
        weight_rounded = round(weight, max_ai31_length)
        f_str = str(weight_rounded)
        f_str_parts = f_str.split(".")
        whole_str = f_str_parts[0].lstrip("0")
        if len(f_str_parts) == 1:
            decimal_str = ""
        else:
            decimal_str = f_str_parts[1].rstrip("0")
        weight_flat_str = whole_str + decimal_str
        if len(weight_flat_str) > max_ai31_length:
            raise UserError(
                _(
                    "The weight specified '%(weight)s' is too large to be represented "
                    "in GS1 standard. Maximum is 6 digits counting both the "
                    "integer and decimal digits. Please correct it."
                )
                % {"weight": weight}
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

        weight = data.get("weight", 0)
        if weight:
            weight_ai, weight_value = self._get_weight_ai31(weight)
            res[weight_ai] = weight_value
        return res

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
                        "The value of GS1 AI %(key)s "
                        "is too long (max %(length)s characters)"
                    )
                    % {"key": key, "length": length}
                )
            res.append(key + value)
            if fnc1_required and i < len(gs1):
                res.append(fnc1)
        return requests.utils.quote("".join(res))

    @api.model  # noqa: C901
    def _get_report_values(self, docids, data=None):  # noqa: C901
        if not data:
            raise UserError(_("Expected data to be passed to the report"))

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
        func_name = "_prepare_%s_values" % model.replace(".", "_")
        func = getattr(self, func_name, None)
        if not func:
            raise UserError(
                _("The model '%(model)s' is not supported by this report.")
                % {"model": model}
            )
        docs1 = func(data_params)

        # generate label data
        docs = []
        for doc in docs1:
            product, lot = doc["product"], doc["lot"]
            if barcode_type in ("gs1-128", "gs1-datamatrix"):
                gs1_barcode = self._prepare_gs1_values(doc)
                if not gs1_barcode:
                    continue
                barcode_string = self._get_gs1_barcode_string(gs1_barcode, barcode_type)
                doc["barcode_values"] = gs1_barcode
                doc["barcode_string"] = barcode_string
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
