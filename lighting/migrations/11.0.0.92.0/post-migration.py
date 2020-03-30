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

    source_lines = env['lighting.product.source.line'].search([
        '|', '|',
        ('color_temperature_ids', '!=', False),
        ('luminous_flux1', '!=', 0),
        ('luminous_flux2', '!=', 0),
    ]).sorted(lambda x: x.source_id.product_id.reference)
    if source_lines:
        ctemp0 = env['lighting.product.color.temperature'].search([
            ('value', '=', 0),
        ])
        if not ctemp0:
            ctemp0 = env['lighting.product.color.temperature'].create({
                'value': 0,
            })
        ctemp1 = env['lighting.product.color.temperature'].search([
            ('value', '=', -1),
        ])
        if not ctemp1:
            ctemp1 = env['lighting.product.color.temperature'].create({
                'value': -1,
            })

    N = len(source_lines)
    for i, sl in enumerate(source_lines, 1):
        _logger.info("Migrating source line of product %s %i/%i" % (
            sl.source_id.product_id.reference, i, N))

        values = {}
        is_tunable = (sl.luminous_flux1 == 0 and sl.luminous_flux2 != 0) or \
                     (sl.luminous_flux1 != 0 and sl.luminous_flux2 != 0)
        if sl.is_color_temperature_flux_tunable != is_tunable:
            values.update({
                'is_color_temperature_flux_tunable': is_tunable,
            })

        flux_values = list(filter(None, [sl.luminous_flux1, sl.luminous_flux2])) or [0]
        fluxes = env['lighting.product.flux']
        for flux_value in flux_values:
            flux = fluxes.search([
                ('value', '=', flux_value),
            ])
            if not flux:
                flux = fluxes.create({
                    'value': flux_value,
                })
            fluxes += flux

        ctemps = sl.color_temperature_ids.sorted(lambda x: x.value)

        if len(fluxes) == 2 and len(ctemps) == 1:
            ctemps = ctemp0 + ctemps
        elif len(fluxes) == 2 and len(ctemps) == 0:
            ctemps = ctemp1 + ctemp0
        elif len(fluxes) == 1 and len(ctemps) == 0:
            ctemps = ctemp0
        elif len(fluxes) == len(ctemps):
            pass
        else:
            raise Exception("Line %i: Not matching K-lm pairs '%s' vs '%s'" % (
                sl.id, ctemps.mapped('value'), fluxes.mapped('value')))

        ct_values = []
        for ct, flux in zip(ctemps, fluxes):
            ctf = env['lighting.product.source.line.color.temperature.flux'].search([
                ('source_line_id', '=', sl.id),
                ('color_temperature_id', '=', ct.id),
                ('flux_id', '=', flux.id),
            ])
            if not ctf:
                ctf_err = env['lighting.product.source.line.color.temperature.flux'].search([
                    ('source_line_id', '=', sl.id),
                    '|', '&',
                    ('color_temperature_id', '=', ct.id),
                    ('flux_id', '!=', flux.id),
                    '&',
                    ('color_temperature_id', '!=', ct.id),
                    ('flux_id', '=', flux.id),
                ])
                if ctf_err:
                    raise Exception("Found partial match on source line %i, reference %s "
                                    "with new ct: %i, flux: %i vs ct: %i, flux: %i" % (
                                        ctf_err.source_line_id.id,
                                        ctf_err.source_line_id.source_id.product_id.reference,
                                        ct.value, flux.value, ctf_err.color_temperature_id.value, ctf_err.flux_id.value
                                    ))
                ct_values.append({
                    'color_temperature_id': ct.id,
                    'flux_id': flux.id,
                })

        if ct_values:
            values.update({
                'color_temperature_flux_ids': [(0, False, x) for x in ct_values]
            })

        if values:
            sl.write(values)
