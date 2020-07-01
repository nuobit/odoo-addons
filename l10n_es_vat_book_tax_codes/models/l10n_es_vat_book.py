# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models

from odoo.tools import ormcache


class L10nEsVatBook(models.Model):
    _inherit = 'l10n.es.vat.book'

    @ormcache('tax_template', 'company_id')
    def _get_tax_id_from_tax_template(self, tax_template, company_id):
        res = super(L10nEsVatBook, self)._get_tax_id_from_tax_template(tax_template, company_id)

        return (res and [res] or []) + self.env['account.tax'].search([
            ('company_id', '=', company_id),
            ('description', '=', tax_template.description),
        ]).mapped('id')

    def get_taxes_from_templates(self, tax_templates):
        company_id = self.company_id.id or self.env.user.company_id.id
        tax_ids = []
        for tmpl in tax_templates:
            tax_ids += self._get_tax_id_from_tax_template(tmpl, company_id)

        return self.env['account.tax'].browse(tax_ids)
