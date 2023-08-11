# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "CRM Lost Stage",
    "summary": "This module adds lost stage",
    "version": "14.0.1.0.1",
    "category": "Sales/CRM",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": ["crm"],
    "data": [
        "data/crm_stage_data.xml",
        "views/crm_stage_views.xml",
        "views/crm_lead_views.xml",
    ],
    "post_init_hook": "migrate_existing_lost_leads",
}
