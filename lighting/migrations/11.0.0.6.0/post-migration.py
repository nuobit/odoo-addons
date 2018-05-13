# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    prods_brand = env['lighting.product'].search([('auxiliary_equipment_brand_id', '!=', False)])

    for product in prods_brand:
        product.auxiliary_equipment_model_ids = [
            (0, False, {'brand_id': x.id}) for x in product.auxiliary_equipment_brand_id]
