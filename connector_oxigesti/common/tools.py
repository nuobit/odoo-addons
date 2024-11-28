# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
import hashlib

from odoo import _
from odoo.exceptions import ValidationError
from odoo.osv.expression import normalize_domain

OP_MAP = {
    "&": "AND",
    "|": "OR",
    "!": "NOT",
}


def domain_prefix_to_infix(domain):
    stack = []
    i = len(domain) - 1
    while i >= 0:
        item = domain[i]
        if item in OP_MAP:
            if item == "!":
                stack.append((item, stack.pop()))
            else:
                stack.append((stack.pop(), item, stack.pop()))
        else:
            if not isinstance(item, (tuple, list)):
                raise ValidationError(_("Unexpected domain clause %s") % item)
            stack.append(item)
        i -= 1
    return stack.pop()


def domain_infix_to_where(domain):
    def _convert_operator(operator, value):
        if value is None:
            if operator == "=":
                operator = "is"
            elif operator == "!=":
                operator = "is not"
            else:
                raise ValidationError(
                    _("Operator '%s' is not implemented on NULL values") % operator
                )
        return operator

    def _domain_infix_to_where_raw(domain, values):
        if not isinstance(domain, (list, tuple)):
            raise ValidationError(_("Invalid domain format %s") % domain)
        if len(domain) == 2:
            operator, expr = domain
            if operator not in OP_MAP:
                raise ValidationError(
                    _("Invalid format, operator not supported %s on domain %s")
                    % (operator, domain)
                )
            values_r, right = _domain_infix_to_where_raw(expr, values)
            return values_r, f"{OP_MAP[operator]} ({right})"
        elif len(domain) == 3:
            expr_l, operator, expr_r = domain
            if operator in OP_MAP:
                values_l, left = _domain_infix_to_where_raw(expr_l, values)
                values_r, right = _domain_infix_to_where_raw(expr_r, values)
                return {**values_l, **values_r}, f"({left} {OP_MAP[operator]} {right})"
            field, operator, value = domain
            # field and values
            if field not in values:
                values[field] = {"next": 1, "values": {}}
            field_n = f"{field}{values[field]['next']}"
            if field_n in values[field]["values"]:
                raise ValidationError(_("Unexpected!! Field %s already used") % field)
            values[field]["values"][field_n] = value
            values[field]["next"] += 1
            # operator and nulls values
            operator = _convert_operator(operator, value)
            return values, f"{field} {operator} %({field_n})s"
        else:
            raise ValidationError(_("Invalid domain format %s") % domain)

    values, where = _domain_infix_to_where_raw(domain, {})
    values_norm = {}
    for _k, v in values.items():
        values_norm.update(v["values"])
    return values_norm, where


def domain_to_where(domain):
    domain_norm = normalize_domain(domain)
    domain_infix = domain_prefix_to_infix(domain_norm)
    return domain_infix_to_where(domain_infix)


def idhash(external_id):
    if not isinstance(external_id, (tuple, list)):
        raise ValidationError(_("external id must be list or tuple"))
    external_id_hash = hashlib.sha256()
    for e in external_id:
        if isinstance(e, int):
            e9 = str(e)
            if int(e9) != e:
                raise Exception("Unexpected")
        elif isinstance(e, str):
            e9 = e
        elif e is None:
            pass
        else:
            raise Exception("Unexpected type for a key: type %s" % type(e))

        external_id_hash.update(e9.encode("utf8"))

    return external_id_hash.hexdigest()
