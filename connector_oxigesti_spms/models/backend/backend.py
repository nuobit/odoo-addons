# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class OxigestiSPMSBackend(models.Model):
    _name = "oxigesti.spms.backend"
    _inherit = "connector.extension.backend"
    _description = "Oxigesti SPMS Backend"

    # TODO: Move to base.backend.sql.adapter.crud

    # databases connnection
    db_name = fields.Char(
        string="Database Name",
        required=True,
        help="The name of the database to connect to.",
    )
    db_user = fields.Char(
        string="Database User",
        required=True,
        help="The user to connect to the database.",
    )
    db_password = fields.Char(
        string="Database Password",
        required=True,
        help="The password to connect to the database.",
    )
    db_host = fields.Char(
        string="Database Host",
        required=True,
        help="The host of the database to connect to.",
    )
    db_port = fields.Integer(
        string="Database Port",
        required=True,
        help="The port of the database to connect to.",
        default=1433,
    )

    db_schema = fields.Char(
        string="Database Schema",
        required=True,
        help="The schema of the database to connect to.",
    )

    # Partner import/export fields and methods
    import_partner_since_date = fields.Datetime(
        string="Import Partner Since",
        help="The date from which to import partners.",
    )
    export_partner_since_date = fields.Datetime(
        string="Export Partner Since",
        help="The date from which to export partners.",
    )

    def button_import_partner_since(self):
        for backend in self:
            last_since_date = backend.import_partner_since_date
            backend.import_partner_since_date = fields.Datetime.now()
            self.env["oxigesti.spms.res.partner"].import_partner_since(
                backend, since_date=last_since_date
            )

    def button_export_partner_since(self):
        for backend in self:
            last_since_date = backend.export_partner_since_date
            backend.export_partner_since_date = fields.Datetime.now()
            self.env["oxigesti.spms.res.partner"].export_partner_since(
                backend, since_date=last_since_date
            )

    # Product import/export fields and methods
    import_product_since_date = fields.Datetime(
        string="Import Partner Since",
        help="The date from which to import partners.",
    )
    export_product_since_date = fields.Datetime(
        string="Export Partner Since",
        help="The date from which to export partners.",
    )

    def button_import_product_since(self):
        for backend in self:
            last_since_date = backend.import_product_since_date
            backend.import_product_since_date = fields.Datetime.now()
            self.env["oxigesti.spms.product.product"].import_product_since(
                backend, since_date=last_since_date
            )

    def button_export_product_since(self):
        for backend in self:
            last_since_date = backend.export_product_since_date
            backend.export_product_since_date = fields.Datetime.now()
            self.env["oxigesti.spms.product.product"].export_product_since(
                backend, since_date=last_since_date
            )

    # Sale Order import/export fields and methods
    import_sale_order_since_date = fields.Datetime(
        string="Import Sale Order Since",
        help="The date from which to import sale orders.",
    )
    export_sale_order_since_date = fields.Datetime(
        string="Export Sale Order Since",
        help="The date from which to export sale orders.",
    )

    def button_import_sale_order_since(self):
        for backend in self:
            last_since_date = backend.import_sale_order_since_date
            backend.import_sale_order_since_date = fields.Datetime.now()
            self.env["oxigesti.spms.sale.order"].import_sale_order_since(
                backend, since_date=last_since_date
            )

    def button_export_sale_order_since(self):
        for backend in self:
            last_since_date = backend.export_sale_order_since_date
            backend.export_sale_order_since_date = fields.Datetime.now()
            self.env["oxigesti.spms.sale.order"].export_sale_order_since(
                backend, since_date=last_since_date
            )

    # SPMS Context import/export fields and methods
    import_spms_context_since_date = fields.Datetime(
        string="Import SPMS Context Since",
        help="The date from which to import SPMS contexts.",
    )
    export_spms_context_since_date = fields.Datetime(
        string="Export SPMS Context Since",
        help="The date from which to export SPMS contexts.",
    )

    def button_import_spms_context_since(self):
        for backend in self:
            last_since_date = backend.import_spms_context_since_date
            backend.import_spms_context_since_date = fields.Datetime.now()
            self.env["oxigesti.spms.spms.context"].import_spms_context_since(
                backend, since_date=last_since_date
            )

    def button_export_spms_context_since(self):
        for backend in self:
            last_since_date = backend.export_spms_context_since_date
            backend.export_spms_context_since_date = fields.Datetime.now()
            self.env["oxigesti.spms.spms.context"].export_spms_context_since(
                backend, since_date=last_since_date
            )

    # SPMS Lot import/export fields and methods
    import_spms_lot_since_date = fields.Datetime(
        string="Import SPMS Lot Since",
        help="The date from which to import SPMS lots.",
    )
    export_spms_lot_since_date = fields.Datetime(
        string="Export SPMS Lot Since",
        help="The date from which to export SPMS lots.",
    )

    def button_import_spms_lot_since(self):
        for backend in self:
            last_since_date = backend.import_spms_lot_since_date
            backend.import_spms_lot_since_date = fields.Datetime.now()
            self.env["oxigesti.spms.spms.lot"].import_spms_lot_since(
                backend, since_date=last_since_date
            )

    def button_export_spms_lot_since(self):
        for backend in self:
            last_since_date = backend.export_spms_lot_since_date
            backend.export_spms_lot_since_date = fields.Datetime.now()
            self.env["oxigesti.spms.spms.lot"].export_spms_lot_since(
                backend, since_date=last_since_date
            )

    # SPMS Prescription Type import/export fields and methods
    import_spms_prescription_type_since_date = fields.Datetime(
        string="Import SPMS Prescription Type Since",
        help="The date from which to import SPMS prescription types.",
    )
    export_spms_prescription_type_since_date = fields.Datetime(
        string="Export SPMS Prescription Type Since",
        help="The date from which to export SPMS prescription types.",
    )

    def button_import_spms_prescription_type_since(self):
        for backend in self:
            last_since_date = backend.import_spms_prescription_type_since_date
            backend.import_spms_prescription_type_since_date = fields.Datetime.now()
            self.env[
                "oxigesti.spms.spms.prescription.type"
            ].import_spms_prescription_type_since(backend, since_date=last_since_date)

    def button_export_spms_prescription_type_since(self):
        for backend in self:
            last_since_date = backend.export_spms_prescription_type_since_date
            backend.export_spms_prescription_type_since_date = fields.Datetime.now()
            self.env[
                "oxigesti.spms.spms.prescription.type"
            ].export_spms_prescription_type_since(backend, since_date=last_since_date)

    # SPMS Suspension Reason import/export fields and methods
    import_spms_suspension_reason_since_date = fields.Datetime(
        string="Import SPMS Suspension Reason Since",
        help="The date from which to import SPMS suspension reasons.",
    )
    export_spms_suspension_reason_since_date = fields.Datetime(
        string="Export SPMS Suspension Reason Since",
        help="The date from which to export SPMS suspension reasons.",
    )

    def button_import_spms_suspension_reason_since(self):
        for backend in self:
            last_since_date = backend.import_spms_suspension_reason_since_date
            backend.import_spms_suspension_reason_since_date = fields.Datetime.now()
            self.env[
                "oxigesti.spms.spms.suspension.reason"
            ].import_spms_suspension_reason_since(backend, since_date=last_since_date)

    def button_export_spms_suspension_reason_since(self):
        for backend in self:
            last_since_date = backend.export_spms_suspension_reason_since_date
            backend.export_spms_suspension_reason_since_date = fields.Datetime.now()
            self.env[
                "oxigesti.spms.spms.suspension.reason"
            ].export_spms_suspension_reason_since(backend, since_date=last_since_date)
