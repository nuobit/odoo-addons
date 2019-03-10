# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

import logging

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    _logger.info("Converting old Location values...")

    Product = env['lighting.product']

    env.cr.execute(
        "SELECT id, install_location from lighting_product WHERE install_location is not null"
    )
    n = env.cr.rowcount
    rows = env.cr.fetchall()
    for i, (id, install_location) in enumerate(rows, 1):
        if install_location:
            ext_id = 'product_location_%s'
            elems = []
            if install_location in ('indoor', 'outdoor', 'underwater'):
                elems.append(ext_id % install_location)
            elif install_location in ('indoor_outdoor',):
                elems.append(ext_id % 'indoor')
                elems.append(ext_id % 'outdoor')
            else:
                raise Exception("Value %s not expected!!" % install_location)

            location_ids = []
            for e_id in elems:
                model, location_id = env['ir.model.data'].get_object_reference('lighting', e_id)
                location_ids.append(location_id)

            product = Product.browse(id)
            product.write({
                'location_ids': [(6, False, location_ids)]
            })

        if (i % 50) == 0:
            _logger.info("    Progress converting old Location values %i%%" % int(i / n * 100))

    _logger.info("Old Location values successfully converted")
