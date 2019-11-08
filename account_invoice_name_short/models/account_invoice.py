# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, _
from odoo.exceptions import UserError

import re
from collections import OrderedDict


def group_by_root(values):
    names_d = OrderedDict()
    for i, n in enumerate(values.split(', ')):
        m = re.match(r'^(.*?)([0-9]+)$', n)
        if m:
            root, num = m.group(1) or None, m.group(2)
            if root not in names_d:
                names_d[root] = []
            names_d[root].append((num, int(num)))
        else:
            if n in names_d:
                raise Exception("ja existeix %s" % n)

    return names_d


def group_by_consecutives(values):
    groups, group = [], []
    ant = None
    for t, n in sorted(values, key=lambda x: x[1]):
        if ant is not None:
            if n == ant + 1:
                group.append((t, n))
            else:
                groups.append(group)
                group = [(t, n)]
        else:
            group.append((t, n))

        ant = n

    if group:
        groups.append(group)

    return groups


def group_by_ranges(root, values):
    gv = group_by_consecutives(values)
    res = []
    for g in gv:
        root_str = root or ''
        if len(g) == 1:
            tu = root_str + g[0][0]
        else:
            hh = [root_str + x for x in [g[0][0], g[-1][0]]]
            if len(g) == 2:
                tu = ', '.join(hh)
            else:
                tu = ' - '.join(hh)

        res.append(tu)

    return res


def shorten_long_delimited_string(value):
    k_vals = []
    for k, v in group_by_root(value).items():
        k_vals += group_by_ranges(k, v)

    return ', '.join(k_vals)


def shorten_long_string(value, max=1000):
    name_l = [value[:max]]
    if len(value) > max:
        name_l.append('(...)')

    return ' '.join(name_l)


def shorten_long_vals(vals):
    vals_new = {}
    if vals:
        if 'name' in vals and vals['name'] and vals['name'].strip():
            vals_new['name'] = shorten_long_string(
                shorten_long_delimited_string(vals['name'])
            )

        if 'origin' in vals and vals['origin'] and vals['origin'].strip():
            vals_new['origin'] = shorten_long_delimited_string(vals['origin'])

    return vals_new


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def write(self, vals):
        vals.update(shorten_long_vals(vals))

        return super().write(vals)

    @api.model
    def create(self, vals):
        vals.update(shorten_long_vals(vals))

        return super().create(vals)
