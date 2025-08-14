# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "CRM Lost Stage",
    "summary": "This module adds lost stage",
    "version": "17.0.0.0.0",
    "category": "Sales/CRM",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": ["crm"],
    "data": [
        "data/crm_stage_data.xml",
        "views/crm_stage_views.xml",
        "views/crm_lead_views.xml",
    ],
    "post_init_hook": "migrate_existing_lost_leads",
}
