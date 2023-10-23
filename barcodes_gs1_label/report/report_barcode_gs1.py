# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import UserError, ValidationError

FNC1 = {
    "gs1-128": "\xf1",
    "gs1-datamatrix": "\xe7",
}


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
    def GS1_AI_FORMAT(self):
        return {
            "01": (14, False),
            "10": (20, True),
            "21": (20, True),
        }

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
                    for q in quants.filtered(lambda x: x.product_id == product):
                        docs += [label] * int(q.quantity)
                else:
                    docs.append(label)
            elif product.tracking in ("lot", "serial"):
                if with_stock:
                    for q in quants.filtered(lambda x: x.product_id == product).sorted(
                        lambda x: x.lot_id.name or ""
                    ):
                        docs += [
                            {
                                "product": product,
                                "lot": q.lot_id,
                            }
                        ] * int(q.quantity)
                else:
                    lots = self.env["stock.production.lot"].search(
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
    def _prepare_gs1_values(self, lot):
        res = {}
        if lot.product_id.barcode:
            res["01"] = lot.product_id.barcode.rjust(14, "0")
        if lot.product_id.tracking == "lot":
            res["10"] = lot.name
        elif lot.product_id.tracking == "serial":
            if lot.ref:
                res["10"] = lot.ref
            res["21"] = lot.name
        # elif product.tracking == "none":
        #     ???
        return res

    @api.model  # noqa: C901
    def _get_report_values(self, docids, data=None):  # noqa: C901
        if not data:
            raise UserError(_("Expected data to be passed to the report"))

        model = data["model"]
        docids = data["ids"]

        barcode_type = data["barcode_type"]
        with_stock = data["with_stock"]
        stock_location_ids = data["stock_location_ids"]
        show_price = data["show_price"]
        show_price_currency = data["show_price_currency"]

        cols = data["layout"]["cols"]
        start_cell = data["layout"]["start_cell"]
        labels_page_count = data["layout"]["labels_page_count"]
        label_copies = data["layout"]["label_copies"]

        docs1 = []
        if model == "product.product":
            for doc in (
                self.env[model].browse(docids).sorted(lambda x: x.default_code or "")
            ):
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
                docs1 += self._get_product_lot(doc, quants, with_stock)
        elif model == "stock.production.lot":
            for doc in (
                self.env[model]
                .browse(docids)
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
                        docs1 += [
                            {
                                "product": doc.product_id,
                                "lot": doc,
                            }
                        ] * int(q.quantity)
                else:
                    docs1.append(
                        {
                            "product": doc.product_id,
                            "lot": doc,
                        }
                    )
        elif model == "stock.quant":
            for doc in (
                self.env[model]
                .browse(docids)
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
                docs1 += self._get_product_lot(doc.product_id, quants, with_stock)
        elif model == "stock.inventory.line":
            for doc in (
                self.env[model]
                .browse(docids)
                .sorted(lambda x: x.product_id.default_code or "")
            ):
                quants = self.env["stock.quant"]
                if with_stock:
                    quants = self.env["stock.quant"].search(
                        [
                            ("product_id", "in", doc.product_id.ids),
                            ("location_id.usage", "=", "internal"),
                            ("location_id", "=", doc.location_id.id),
                            ("quantity", ">", 0),
                            ("company_id", "=", self.env.company.id),
                        ]
                    )
                docs1 += self._get_product_lot(doc.product_id, quants, with_stock)
        elif model == "stock.picking":
            qty_tracking = {}
            for ml in (
                self.env[model]
                .browse(docids)
                .mapped("move_ids_without_package")
                .mapped("move_line_ids")
                .filtered(lambda x: x.state == "done")
            ):
                qty_tracking.setdefault(ml.product_id, {}).setdefault(ml.lot_id, 0)
                qty_tracking[ml.product_id][ml.lot_id] += ml.qty_done
            for product, lot_qty in sorted(
                qty_tracking.items(), key=lambda x: x[0].default_code or ""
            ):
                for lot, qty in sorted(lot_qty.items(), key=lambda x: x[0].name or ""):
                    if qty > 0:
                        docs1 += [
                            {
                                "product": product,
                                "lot": lot or None,
                            }
                        ] * int(qty)
        else:
            raise UserError(_("Unexpected model '%s'") % model)

        docs = []
        for doc in docs1:
            product, lot = doc["product"], doc["lot"]

            if barcode_type in ("gs1-128", "gs1-datamatrix"):
                gs1_barcode = self._prepare_gs1_values(lot)
                if not gs1_barcode:
                    continue
                fnc1 = FNC1[barcode_type]
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
                            _("The value of GS1 AI %s is too long (max %s characters)")
                            % (key, length)
                        )
                    res.append(key + value)
                    if fnc1_required and i < len(gs1):
                        res.append(fnc1)
                doc["barcode_values"] = gs1_barcode
                doc["barcode_string"] = "".join(res)
                lot.gs1_generated = True
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
