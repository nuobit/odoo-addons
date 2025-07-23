# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Connector Oxigesti Spms",
    "summary": "This module provides a connector for Oxigesti Spms",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions, S.L.",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "connector_extension_mssql",
        "sale_management",
        "l10n_pt_sale_order_spms",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/backend.xml",
        "data/ir_cron.xml",
        "data/queue_job_channel.xml",
        "data/queue_job_function.xml",
        "views/backend_views.xml",
        "views/res_partner_views.xml",
        "views/product_product_views.xml",
        "views/sale_order_views.xml",
        "views/connector_oxigesti_spms_menu.xml",
        "views/spms_context.xml",
        "views/spms_lot.xml",
        "views/spms_prescription_type.xml",
        "views/spms_suspension_reason.xml",
    ],
}
