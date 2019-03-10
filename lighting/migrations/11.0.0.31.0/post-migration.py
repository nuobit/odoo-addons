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

    # recalculate automatic descriptions
    _logger.info("Converting Sealing values...")

    Product = env['lighting.product']
    Sealing = env['lighting.product.sealing']
    maps_ips = [('ip', 'sealing_id'), ('ip2', 'sealing2_id')]

    env.cr.execute(
        "SELECT id, ip, ip2 from lighting_product WHERE ip !=0 or ip2 !=0"
    )
    rows = env.cr.fetchall()
    for id, ip, ip2 in rows:
        for f0, f1 in maps_ips:
            ip0 = ip if f0 == 'ip' else ip2
            if ip0:
                ip9 = Sealing.search([
                    ('name', '=', 'IP%02d' % ip0)
                ])
                if not ip9:
                    ip9 = Sealing.create({'name': 'IP%02d' % ip0})

                product = Product.browse(id)
                product.write({f1: ip9.id})

    _logger.info("Sealing values successfully converted")
