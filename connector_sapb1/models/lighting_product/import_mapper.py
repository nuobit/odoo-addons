# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)

MAP_CAT_LOC = {'Cristher': 'EXT', 'Dopo': 'EXT', 'Indeluz': 'INT', 'Exo': 'INT'}

MAP_STATUS_MARKETING = {
    'Novedades': 'N',
    'Catalogado': 'C',
    'Descatalogado': 'D',
    'Fe Digital': 'ES',
    'Histórico': 'H',
}


class LigthingProductImportMapper(Component):
    _name = 'sapb1.lighting.product.import.mapper'
    _inherit = 'sapb1.import.mapper'

    _apply_on = 'sapb1.lighting.product'

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def description_manual(self, record):
        if record['ItemName'] and record['ItemName'].strip():
            return {'description_manual': record['ItemName'].strip()}

    @mapping
    def ean(self, record):
        if record['CodeBars'] and record['CodeBars'].strip():
            return {'ean': record['CodeBars'].strip()}

    @mapping
    def stock(self, record):
        values = {}

        values['onhand_qty'] = record['OnHand']
        values['commited_qty'] = record['IsCommited']

        capacity_qty = record['Capacity'] > 0 and record['Capacity'] or 0
        values['capacity_qty'] = capacity_qty

        available_qty = (record['OnHand'] or 0) - (record['IsCommited'] or 0)
        values['available_qty'] = (available_qty > 0 and available_qty or 0) + capacity_qty

        values['onorder_qty'] = record['OnOrder']

        values['stock_future_date'] = record['ShipDate']
        values['stock_future_qty'] = record['ShipDate'] and (available_qty + (record['OnOrder'] or 0)) or 0

        if values:
            return values

    @mapping
    def last_purchase_date(self, record):
        if record['LastPurDat']:
            return {'last_purchase_date': record['LastPurDat']}

    @mapping
    def dimensions(self, record):
        values = {}
        values['ibox_weight'] = record['SWeight1']
        values['ibox_volume'] = record['SVolume'] * 1000
        values['ibox_length'] = record['SLength1']
        values['ibox_width'] = record['SWidth1']
        values['ibox_height'] = record['SHeight1']
        if values:
            return values

    @only_create
    @mapping
    def state_marketing_state(self, record):
        u_acc_obsmark = record['U_ACC_Obsmark'] and record['U_ACC_Obsmark'].strip() or None
        if u_acc_obsmark:
            state_marketing = MAP_STATUS_MARKETING.get(u_acc_obsmark)
            if state_marketing:
                return {
                    'state_marketing': state_marketing,
                    'state': 'published',
                }

        return {
            'state': 'draft',
        }

    def _get_sibling_reference(self, reference, pattern):
        m = re.match(pattern, reference)
        if not m:
            raise Exception(_("Reference format unexpected '%s'") % reference)

        reference_prefix = m.group(1)
        references = self.env['lighting.product'].search([
            ('reference', '=like', '%s%%' % reference_prefix),
        ])

        return references

    @only_create
    @mapping
    def catalog_and_location(self, record):
        catalogs = None
        itms_grp_name = record['ItmsGrpNam'] and record['ItmsGrpNam'].strip() or None
        if not itms_grp_name:
            references = self._get_sibling_reference(record['ItemCode'].strip(), "^(.+)-[^-]{2}")
            if references:
                catalogs = references.mapped('catalog_ids')
        else:
            domain = []
            if itms_grp_name != 'Accesorios':
                domain.append(
                    ('name', '=ilike', itms_grp_name),
                )
            catalogs = self.env['lighting.catalog'].search(domain)
        if not catalogs:
            raise Exception(_("Catalog '%s' not found and cannot be inferred") % itms_grp_name)

        location_codes = [MAP_CAT_LOC[x] for x in catalogs.mapped('name')]
        locations = self.env['lighting.product.location'].search([
            ('code', 'in', location_codes),
        ])
        if not locations:
            raise Exception(_("Locations with codes '%s' not found and cannot be inferred") % location_codes)

        return {
            'catalog_ids': [(6, False, catalogs.mapped('id'))],
            'location_ids': [(6, False, locations.mapped('id'))],
        }

    @only_create
    @mapping
    def family_ids(self, record):
        families = None
        familia = record['U_U_familia'] and record['U_U_familia'].strip() or None
        familia = familia != '-' and familia or None
        if not familia:
            item_code = record['ItemCode'].strip()
            references = self._get_sibling_reference(item_code, "^(.+)-[^-]{2}")
            if references:
                families = references.mapped('family_ids')

            if not families:
                references = self._get_sibling_reference(item_code, "^([^-]+)-.+$")
                if not references:
                    references = self._get_sibling_reference(item_code, "^([0-9]{3})[A-Z]-.+$")
                if references:
                    reference_groups = {}
                    for r in references:
                        for f in r.family_ids:
                            reference_groups.setdefault(f, 0)
                            reference_groups[f] += 1
                    if reference_groups:
                        families = sorted(reference_groups.items(),
                                          key=lambda x: x[1], reverse=True)[0][0]
        else:
            families = self.env['lighting.product.family'].search([
                ('name', '=ilike', familia),
            ])

        if not families:
            raise Exception(_("Family '%s' not found and it cannot be inferred") % familia)

        return {'family_ids': [(6, False, families.mapped('id'))]}

    @only_create
    @mapping
    def category_id(self, record):
        category = None
        aplicacion = record['U_U_aplicacion'] and record['U_U_aplicacion'].strip() or None
        if not aplicacion:
            references = self._get_sibling_reference(record['ItemCode'].strip(), "^(.+)-[^-]{2}")
            if references:
                category = references.mapped('category_id')
                if len(category) > 1:
                    raise Exception(_("The other variants have more than one category '%s', "
                                      "it's not possible to infer the category.") % (category,))
        else:
            complete_name = aplicacion
            m = re.match(r'^([^/]+) *\/ *(.+)$', aplicacion)
            if m:
                complete_name = ' / '.join(m.groups())

            category = self.env['lighting.product.category'] \
                .with_context(lang='es_ES') \
                .search([('complete_name', '=ilike', complete_name)])
            if len(category) > 1:
                raise Exception(_("Multiple Category %s found") % (', '.join(category.mapped('name')),))

        if not category:
            catalog_name = record['ItmsGrpNam'] and record['ItmsGrpNam'].strip() or None
            if catalog_name == 'Accesorios':
                category = self.env['lighting.product.category'] \
                    .with_context(lang='es_ES') \
                    .search([
                    ('parent_id', '=', False),
                    ('name', '=', 'Accesorios'),
                ])
                if len(category) > 1:
                    raise Exception(_("Multiple Accessory category %s found") % (', '.join(category.mapped('name')),))

        if not category:
            raise Exception(_("Category '%s' not found and it cannot be inferred") % aplicacion)

        return {'category_id': category.id}

    @only_create
    @mapping
    def reference(self, record):
        return {'reference': record['ItemCode'] and record['ItemCode'].strip() or None}
