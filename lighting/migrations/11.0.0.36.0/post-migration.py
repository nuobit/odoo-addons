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
    _logger.info("Converting Color temperature values...")

    SourceLine = env['lighting.product.source.line']
    ColorTemperature = env['lighting.product.color.temperature']

    env.cr.execute(
        "SELECT id, color_temperature from lighting_product_source_line WHERE color_temperature != 0"
    )
    n = env.cr.rowcount
    th = int(n / 100) or 1
    rows = env.cr.fetchall()
    for i, (id, color_temperature) in enumerate(rows, 1):
        if color_temperature:
            color_temperature_id = ColorTemperature.search([
                ('value', '=', color_temperature)
            ])
            if not color_temperature_id:
                color_temperature_id = ColorTemperature.create({'value': color_temperature})

            source_line = SourceLine.browse(id)
            source_line.write({'color_temperature_id': color_temperature_id.id})

        if (i % th) == 0:
            _logger.info(" - Progress Converting Color temperature values %i%%" % (int(i / n * 100)))

    _logger.info("Color temperature values successfully converted")
