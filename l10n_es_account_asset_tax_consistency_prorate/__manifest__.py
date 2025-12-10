# Copyright NuoBiT Solutions SL - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "L10n ES - Account Tax Consistency Prorate",
    "summary": "This module adds in taxes of l10n_es_special_prorate "
    "data account asset tax consistency selection field",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_special_prorate",
        "account_asset_tax_consistency",
    ],
    "post_init_hook": "post_init_hook",
    "auto_install": True,
}
