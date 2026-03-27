# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import datetime
import hashlib
import unicodedata

from lxml import html

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.connector_extension.common.tools import color_rgb2hex

# Elements the HTML editor leaves around nothing to show. A value made only of
# these, with no text, is blank; any other element (an image, a table, a rule,
# an embed...) is content whatever its text: never a loss of content.
BLANK_HTML_TAGS = frozenset(
    {
        "p",
        "div",
        "span",
        "br",
        "b",
        "strong",
        "i",
        "em",
        "u",
        "s",
        "strike",
        "font",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "ul",
        "ol",
        "li",
        "blockquote",
        "pre",
        "code",
        "sub",
        "sup",
        "small",
        "mark",
        "a",
        "section",
        "article",
        "header",
        "footer",
    }
)


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
            raise Exception(f"Unexpected type for a key: type {type(e)}")
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
            if not isinstance(value, (tuple | list)):
                raise ValidationError(
                    _(
                        "Operator '%(OPERATOR)s' only supports"
                        " tuples or lists, not %(TYPES)s"
                    )
                    % {
                        "OPERATOR": op,
                        "TYPES": type(value),
                    }
                )
            if field in res:
                raise ValidationError(
                    _("Duplicated field %(field)s") % {"field": field}
                )
            res[field] = self._normalize_value(value)
        elif op in (">", ">=", "<", "<="):
            if not isinstance(value, (datetime.date | datetime.datetime | int)):
                raise ValidationError(
                    _("Type %(OPERATOR)s not supported for operator %(TYPES)s")
                    % {
                        "OPERATOR": op,
                        "TYPES": type(value),
                    }
                )
            if op in (">", "<"):
                adj = 1
                if isinstance(value, (datetime.date | datetime.datetime)):
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


def is_blank_html(value):
    """Whether an HTML value has nothing to show.

    ``value`` is what an Odoo Text field edited with the HTML widget holds:
    ``False`` when empty, else the markup as typed (the editor writes
    ``<p><br></p>`` for an untouched field). Blank means no text once
    whitespace is collapsed (no-break spaces included; the parser decodes
    the entities) and every element in ``BLANK_HTML_TAGS``; attributes are
    ignored. lxml's HTML parser recovers from malformed markup, so stray
    characters are text, and text is content.
    """
    if not value:
        # An empty Odoo Text field holds False; "" and None are the same
        # absence in the callers' hands. This is the one place deciding it.
        blank = True
    else:
        root = html.fragment_fromstring(value, create_parent="div")
        text = "".join(root.itertext())
        blank = not text.strip() and all(
            isinstance(element.tag, str) and element.tag in BLANK_HTML_TAGS
            for element in root.iter()
        )
    return blank


def prepare_html(value):
    """The HTML value the connectors export for an HTML-edited field.

    ``None`` when the value is missing or blank (``is_blank_html``): the
    adapter represents the absence on the wire. Otherwise the value
    with its ``rgb()`` colours converted to hex, as WooCommerce expects.
    """
    return color_rgb2hex(value) if not is_blank_html(value) else None
