# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
import datetime
import hashlib
import re
import unicodedata

from odoo import _
from odoo.exceptions import ValidationError


def list2hash(_list):
    _hash = hashlib.sha256()
    for e in _list:
        if isinstance(e, int):
            e9 = str(e)
        elif isinstance(e, str):
            e9 = e
        elif isinstance(e, float):
            e9 = str(e)
        elif e is None:
            e9 = ""
        else:
            raise Exception("Unexpected type for a key: type %s" % type(e))
        _hash.update(e9.encode("utf8"))
    return _hash.hexdigest()


def domain_to_normalized_dict(self, domain):
    """Convert, if possible, standard Odoo domain to a dictionary.
    To do so it is necessary to convert all operators to
    equal '=' operator.
    """
    res = {}
    for elem in domain:
        if len(elem) != 3:
            raise ValidationError(_("Wrong domain clause format %s") % elem)
        field, op, value = elem
        if op == "=":
            if field in res:
                raise ValidationError(_("Duplicated field %s") % field)
            res[field] = self._normalize_value(value)
        elif op == "!=":
            if not isinstance(value, bool):
                raise ValidationError(
                    _("Not equal operation not supported for non boolean fields")
                )
            if field in res:
                raise ValidationError(_("Duplicated field %s") % field)
            res[field] = self._normalize_value(not value)
        elif op == "in":
            if not isinstance(value, (tuple, list)):
                raise ValidationError(
                    _(
                        "Operator '%(OPERATOR)s' only supports tuples or lists, not %(TYPES)s"
                    )
                    % {
                        "OPERATOR": op,
                        "TYPES": type(value),
                    }
                )
            if field in res:
                raise ValidationError(_("Duplicated field %s") % field)
            res[field] = self._normalize_value(value)
        elif op in (">", ">=", "<", "<="):
            if not isinstance(value, (datetime.date, datetime.datetime, int)):
                raise ValidationError(
                    _("Type %(type)s not supported for operator %(op)s")
                    % dict(type=value, op=op)
                )
            if op in (">", "<"):
                adj = 1
                if isinstance(value, (datetime.date, datetime.datetime)):
                    adj = datetime.timedelta(days=adj)
                if op == "<":
                    op, value = "<=", value - adj
                else:
                    op, value = ">=", value + adj

            res[field] = self._normalize_value(value)
        else:
            raise ValidationError(_("Operator %s not supported") % op)

    return res


def convert_item_to_json(item, ct, namespace):
    jitem = {}
    for path, func, key, multi in ct:
        if key in jitem:
            raise ValidationError(_("Key %s already exists") % key)
        value = item.xpath(path, namespaces=namespace)
        if not value:
            jitem[key] = None
        else:
            if multi:
                jitem[key] = func(value)
            else:
                if len(value) > 1:
                    raise ValidationError(_("Multiple values found for '%s'") % path)
                else:
                    jitem[key] = func(value[0])
    return jitem


def convert_to_json(data, ct, namespace):
    res = []
    for d in data:
        res.append(convert_item_to_json(d, ct, namespace))
    return res


def slugify(value):
    if not value:
        return None
    return (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
        .replace(" ", "")
    )


def trim_domain(domain):
    trimmed_domain = []
    for d in domain:
        if isinstance(d, (list, tuple)):
            if len(d) == 3 and isinstance(d[2], str):
                trimmed_domain.append((d[0], d[1], d[2].strip()))
            elif len(d) == 3 and isinstance(d[2], (list, tuple)):
                trimmed_value = [
                    value.strip() if isinstance(value, str) else value for value in d[2]
                ]
                trimmed_domain.append((d[0], d[1], trimmed_value))
            else:
                trimmed_domain.append(d)
        else:
            raise Exception("Unexpected domain format: %s" % d)
    return trimmed_domain


def color_rgb2hex(data):
    def conv_rgb(match):
        rgb_hex_l = []
        groups = match.groups()
        for value, percent in zip(groups[0::2], groups[1::2]):
            if percent:
                hex_value = round(float(value) * 255 / 100)
            else:
                hex_value = int(value)
            rgb_hex_l.append(f"{hex_value:02X}")
        return f'#{"".join(rgb_hex_l)}'

    return re.sub(
        r"rgb\( *([0-9.]+) *(%?) *, *([0-9.]+) *(%?) *, *([0-9.]+) *(%?) *\)",
        conv_rgb,
        data,
        flags=re.IGNORECASE,
    )
