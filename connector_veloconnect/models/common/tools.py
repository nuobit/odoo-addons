# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import datetime
import hashlib
import unicodedata

from odoo import _
from odoo.odoo.exceptions import ValidationError


def list2hash(l):
    hash = hashlib.sha256()
    for e in l:
        if isinstance(e, int):
            e9 = str(e)
        elif isinstance(e, str):
            e9 = e
        #     to_delete?
        elif isinstance(e, float):
            e9 = str(e)
        elif e is None:
            e9 = ''
        else:
            raise Exception("Unexpected type for a key: type %" % type(e))
        hash.update(e9.encode('utf8'))
    return hash.hexdigest()


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
                    _("Operator '%s' only supports tuples or lists, not %s")
                    % (op, type(value))
                )
            if field in res:
                raise ValidationError(_("Duplicated field %s") % field)
            res[field] = self._normalize_value(value)
        elif op in (">", ">=", "<", "<="):
            if not isinstance(
                value, (datetime.date, datetime.datetime, int)
            ):
                raise ValidationError(
                    _("Type {} not supported for operator {}").format(
                        type(value), op
                    )
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

def convert_to_json(data, ct, namespace):
    res = []
    for d in data:
        jitem = {}
        for path, func, key, multi in ct:
            if key in jitem:
                raise ValidationError(_("Key %s already exists") % key)
            value = d.xpath(path, namespaces=namespace)
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
        res.append(jitem)
    return res

def slugify(value):
    if not value:
        return None
    return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii').lower().replace(' ', '')
