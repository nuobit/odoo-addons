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
    _logger.info("Moving CRI to sources...")

    SourceLine = env['lighting.product.source.line']

    env.cr.execute(
        "SELECT id, reference, cri_min from lighting_product WHERE cri_min != 0"
    )
    n = env.cr.rowcount
    th = int(n / 100) or 1
    rows = env.cr.fetchall()
    for i, (id, reference, cri_min) in enumerate(rows, 1):
        if cri_min:
            source_line = SourceLine.search([
                ('source_id.product_id', '=', id),
                ('source_id.relevance', '=', 'main'),
                ('is_led', '=', True),
                ('is_integrated', '=', True),
            ]).sorted(lambda x: (x.sequence, x.id))
            if source_line:
                source_line[0].cri_min = cri_min
                if len(source_line) != 1:
                    _logger.warning("Product %s has %i source line candidates, "
                                    "only the first source line (sequence %i) has been populated with CRI %i"
                                    % (reference, len(source_line), source_line[0].sequence, cri_min))
            else:
                _logger.warning("Product %s has no source line candidate, "
                                "so the CRI value %i has been lost" % (reference, cri_min))

        if (i % th) == 0:
            _logger.info(" - Progress moving CRI to sources %i%%" % (int(i / n * 100)))

    _logger.info("CRI successfully moved to sources")
