# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from dateutil import relativedelta

from odoo import _, fields, models


class OrderpointSyncTemplate(models.Model):
    """ Defines Minimum stock rules. """

    _name = "stock.warehouse.orderpoint.sync.template"
    _description = "Minimum Inventory Rule sync template"

    name = fields.Char(copy=False, required=True)
    active = fields.Boolean(
        "Active",
        default=True,
        help="If the active field is set to False, "
        "it will allow you to hide the orderpoint without removing it.",
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse", "Warehouse", ondelete="cascade", required=True
    )
    location_ids = fields.Many2many(
        string="Locations",
        comodel_name="stock.location",
        relation="stock_warehouse_orderpoint_sync_template_location_rel",
        column1="template_id",
        column2="location_id",
        required=True,
    )
    route_ids = fields.Many2many(
        string="Routes",
        comodel_name="stock.location.route",
        relation="stock_warehouse_orderpoint_sync_template_route_rel",
        column1="template_id",
        column2="route_id",
        required=False,
    )

    group_id = fields.Many2one(
        "procurement.group",
        "Procurement Group",
        copy=False,
        help="Moves created through this orderpoint will be put in this "
        "procurement group. If none is given, the moves generated "
        "by procurement rules will be grouped into one big picking.",
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )

    last_update = fields.Datetime(readonly=True)
    status = fields.Char(readonly=True)

    line_ids = fields.One2many(
        comodel_name="stock.warehouse.orderpoint.sync.template.line",
        inverse_name="sync_template_id",
        copy=True,
    )

    orderpoint_count = fields.Integer(
        compute="_compute_orderpoint_count", string="Orderpoint(s)"
    )

    def copy(self, default=None):
        self.ensure_one()
        default = dict(
            default or {},
            name=_("%s (copy)") % self.name,
        )

        return super().copy(default)

    def _compute_orderpoint_count(self):
        for rec in self:
            rec.orderpoint_count = self.env["stock.warehouse.orderpoint"].search_count(
                [("sync_template_line_id.sync_template_id", "=", rec.id)]
            )

    def create_orderpoints(self):  # noqa: C901
        def generate_orderpoint(record, lc):
            created, updated, deleted = 0, 0, 0
            child_ids = self.env["stock.location"].search(
                [("company_id", "=", record.company_id.id), ("location_id", "=", lc.id)]
            )
            if not child_ids:
                # generate reordering rules for the location and for every product
                for p in record.line_ids:
                    ######
                    tmp_location_ids = set(record.location_ids.mapped("id"))

                    to_update = {}
                    pending = []
                    # mark to update
                    for op in p.orderpoint_ids:
                        if op.location_id.id in tmp_location_ids:
                            to_update[op.location_id.id] = op
                            tmp_location_ids.remove(op.location_id.id)
                        else:
                            pending.append(op)

                    # mark to delete
                    to_delete = []
                    for op in pending:
                        if tmp_location_ids:
                            to_update[tmp_location_ids.pop()] = op
                        else:
                            to_delete.append(op)

                    # mark to create
                    to_create = tmp_location_ids

                    #####
                    # update
                    for location_id, op in to_update.items():
                        changed = False
                        # company
                        if op.company_id.id != record.company_id.id:
                            op.company_id = record.company_id.id
                            changed = True
                        # warehouse
                        if op.warehouse_id.id != record.warehouse_id.id:
                            op.warehouse_id = record.warehouse_id.id
                            changed = True
                        # location
                        if op.location_id.id != location_id:
                            op.location_id = location_id
                            changed = True
                        # product
                        if op.product_id.id != p.product_id.id:
                            op.product_id = p.product_id.id
                            changed = True

                        # logistics
                        if op.product_min_qty != p.product_min_qty:
                            op.product_min_qty = p.product_min_qty
                            changed = True
                        if op.product_max_qty != p.product_max_qty:
                            op.product_max_qty = p.product_max_qty
                            changed = True
                        if op.qty_multiple != p.qty_multiple:
                            op.qty_multiple = p.qty_multiple
                            changed = True
                        lead_days, dummy = op.rule_ids._get_lead_days(op.product_id)
                        lead_days_date = (
                            fields.Date.today()
                            + relativedelta.relativedelta(days=lead_days)
                        )
                        if op.lead_days_date != lead_days_date:
                            op.lead_days_date = lead_days_date
                            changed = True

                        if changed:
                            updated += 1

                    # delete
                    for op in to_delete:
                        op.unlink()
                        deleted += 1

                    # create
                    for location_id in to_create:
                        # self.env['stock.warehouse.orderpoint'].create({
                        p.orderpoint_ids = [
                            (
                                0,
                                False,
                                {
                                    "company_id": record.company_id.id,
                                    "location_id": location_id,
                                    "warehouse_id": record.warehouse_id.id,
                                    "group_id": record.group_id,
                                    "product_id": p.product_id.id,
                                    "product_min_qty": p.product_min_qty,
                                    "product_max_qty": p.product_max_qty,
                                    "qty_multiple": p.qty_multiple,
                                },
                            )
                        ]
                        created += 1
            else:
                for c in child_ids:
                    crt, upd, dele = generate_orderpoint(record, c)
                    created += crt
                    updated += upd
                    deleted += dele

            return created, updated, deleted

        for rec in self:
            # orderpoints
            created, updated, deleted = 0, 0, 0
            for loc in rec.location_ids:
                crt, upd, dele = generate_orderpoint(rec, loc)
                created += crt
                updated += upd
                deleted += dele

            # routes
            radded, pupdated = 0, 0
            if rec.route_ids:
                for line in rec.line_ids:
                    changed = False
                    for r in rec.route_ids:
                        if r.id not in line.product_id.route_ids.mapped("id"):
                            line.product_id.route_ids = [(4, r.id, False)]
                            changed = True
                            radded += 1

                    if changed:
                        pupdated += 1

            rec.last_update = fields.Datetime.now()
            rec.status = _(
                "Orderpoints: Created: %i, Updated: %i, Deleted: %i | "
                "Product routes: Routes added: %i, Products updated: %i"
            ) % (created, updated, deleted, radded, pupdated)

    _sql_constraints = [
        (
            "namecomp_uniq",
            "unique (company_id, name)",
            "Name must be unique per company!",
        ),
    ]


class OrderpointSyncTemplateLine(models.Model):
    _name = "stock.warehouse.orderpoint.sync.template.line"
    _description = "Minimum Inventory Rule sync template lines"

    product_id = fields.Many2one(
        "product.product",
        "Product",
        domain=[("type", "=", "product")],
        ondelete="cascade",
        required=True,
    )

    product_uom = fields.Many2one(
        "uom.uom",
        "Product Unit of Measure",
        related="product_id.uom_id",
        readonly=True,
        required=True,
        default=lambda self: self._context.get("product_uom", False),
    )

    product_min_qty = fields.Float(
        "Minimum Quantity",
        digits="Product Unit of Measure",
        required=True,
        help="When the virtual stock goes below the Min Quantity specified for this field,"
        " Odoo generates a procurement to bring the forecasted quantity to the Max Quantity.",
    )
    product_max_qty = fields.Float(
        "Maximum Quantity",
        digits="Product Unit of Measure",
        required=True,
        help="When the virtual stock goes below the Min Quantity, Odoo generates a procurement"
        " to bring the forecasted quantity to the Quantity specified as Max Quantity.",
    )
    qty_multiple = fields.Float(
        "Qty Multiple",
        digits="Product Unit of Measure",
        default=1,
        required=True,
        help="The procurement quantity will be rounded up to this multiple. If it is 0, "
        "the exact quantity will be used.",
    )

    orderpoint_ids = fields.One2many(
        comodel_name="stock.warehouse.orderpoint",
        inverse_name="sync_template_line_id",
        string="Orderpoints",
        copy=True,
    )

    sync_template_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint.sync.template", ondelete="cascade"
    )

    _sql_constraints = [
        (
            "prodtemp_uniq",
            "unique (sync_template_id, product_id)",
            "Product must be unique per template!",
        ),
    ]
