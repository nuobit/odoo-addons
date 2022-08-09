# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, fields, models



class FirstRegularization(models.Model):
    _inherit = "aeat.map.special.prorrate.year"


    regularization = fields.Float(string="First regularization")

    def first_regularization(self):
        a = 1

        acum_472, acum_total = self.check_prorrate()
        a = 1

        self.ensure_one()
        date_from = "%s-01-01" % self.year
        date_to = "%s-12-31" % self.year
        mod303 = self.env["l10n.es.aeat.mod303.report"].new({})
        affected_taxes = [
            "l10n_es_special_prorate.account_tax_template_p_priva10_bc",
            "l10n_es_special_prorate.account_tax_template_p_priva10_bi",
            "l10n_es_special_prorate.account_tax_template_p_priva10_ibc",
            "l10n_es_special_prorate.account_tax_template_p_priva10_ibi",
            "l10n_es_special_prorate.account_tax_template_p_priva10_ic_bc",
            "l10n_es_special_prorate.account_tax_template_p_priva10_ic_bi",
            "l10n_es_special_prorate.account_tax_template_p_priva10_sc",
            "l10n_es_special_prorate.account_tax_template_p_priva10_sp_in",
            "l10n_es_special_prorate.account_tax_template_p_priva21_bc",
            "l10n_es_special_prorate.account_tax_template_p_priva21_bi",
            "l10n_es_special_prorate.account_tax_template_p_priva21_ibc",
            "l10n_es_special_prorate.account_tax_template_p_priva21_ibi",
            "l10n_es_special_prorate.account_tax_template_p_priva21_ic_bc",
            "l10n_es_special_prorate.account_tax_template_p_priva21_ic_bi",
            "l10n_es_special_prorate.account_tax_template_p_priva21_sc",
            "l10n_es_special_prorate.account_tax_template_p_priva21_sp_in",
            "l10n_es_special_prorate.account_tax_template_p_priva4_bc",
            "l10n_es_special_prorate.account_tax_template_p_priva4_bi",
            "l10n_es_special_prorate.account_tax_template_p_priva4_ibc",
            "l10n_es_special_prorate.account_tax_template_p_priva4_ibi",
            "l10n_es_special_prorate.account_tax_template_p_priva4_ic_bc",
            "l10n_es_special_prorate.account_tax_template_p_priva4_ic_bi",
            "l10n_es_special_prorate.account_tax_template_p_priva4_sc",
            "l10n_es_special_prorate.account_tax_template_p_priva4_sp_in",
        ]
        MapLine = self.env["l10n.es.aeat.map.tax.line"]
        mapline_vals = {
            "move_type": "all",
            "field_type": "base",
            "sum_type": "both",
            "exigible_type": "yes",
            "tax_ids": [(4, self.env.ref(x).id) for x in affected_taxes],
        }

        map_line = MapLine.new(mapline_vals)
        move_lines = mod303._get_tax_lines(date_from, date_to, map_line)
        total = 0.0
        list_ids = []
        move_lines_filtered = move_lines.filtered(lambda x: x.account_id.id == 11540)
        list_tax = [545, 548, 585, 588, 573, 576, 543, 570, 541, 547, 586, 589, 574, 577, 542, 571, 546, 549, 584, 587,
                    572, 575, 544, 569]
        for m in move_lines_filtered:
            total += m.balance
        for m in move_lines:
            total += (m.balance * (m.tax_ids.filtered(lambda x: x.id in list_tax).amount / 100)) * 0.15
        b = 2
        taxed = sum(move_lines.mapped("credit")) - sum(move_lines.mapped("debit"))
        # Get base amount of exempt operations

    def check_prorrate(self):
        taxes = {545, 548, 585, 588, 573, 576, 543, 570, 541, 547, 586, 589, 574, 577, 542, 571, 546, 549, 584, 587,
                 572, 575, 544, 569}
        # taxes = {546}
        acum_472 = {}
        acum_base = {}

        for m in self.env['account.move'].search(
            [('date', '>=', '2021-01-01'), ('date', '<=', '2021-12-31'), ('company_id', '=', 5),
             ('state', '=', 'posted'), '|', ('line_ids.tax_ids', 'in', list(taxes)),
             ('line_ids.tax_line_id', 'in', list(taxes)), ('id', 'not in', [602501])]):
            x = 0.0
            y = 0.0

            for move_line in m.line_ids.filtered(lambda x: x.tax_ids or x.tax_line_id):
                if move_line.tax_line_id:
                    if move_line.tax_ids:
                        raise Exception("Taxes ids not allowed")
                    if move_line.tax_line_id.id in taxes:
                        if move_line.tax_repartition_line_id.account_id == move_line.account_id:
                            acum_472.setdefault(move_line.tax_line_id, 0)
                            acum_472[move_line.tax_line_id] += move_line.balance
                            x += move_line.balance
                else:
                    if not move_line.tax_ids:
                        raise Exception("tax_ids not found.")
                    base_tax_id = set(move_line.tax_ids.ids) & taxes
                    base_tax = self.env['account.tax'].browse(base_tax_id)
                    if len(base_tax) > 1:
                        raise Exception("More than one tax")
                    if base_tax:
                        acum_base.setdefault(base_tax, 0)
                        # acum_total.setdefault(move_line.tax_ids.id, 0)
                        acum_base[base_tax] += round(move_line.balance * base_tax.amount / 100 * 0.18, 2)
                        y += round(move_line.balance * base_tax.amount / 100 * 0.18, 2)
            if x != y:
                if x - y > 0.05 or x - y < -0.05:
                    raise Exception("Error in move %s" % m.id)

                # raise Exception("Error")
        return acum_472, acum_base
