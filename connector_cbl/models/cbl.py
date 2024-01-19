# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import datetime
import json
import logging
import re

import requests
from lxml import etree

from odoo import _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


def xpath1(tree, xpath):
    tag_l = tree.xpath(xpath)
    if len(tag_l) == 0:
        raise ValidationError(_("No elements found on xpath: %s" % xpath))
    if len(tag_l) != 1:
        raise ValidationError(
            _(
                "Expected 1 element, %(elements)s found on  "
                "xpath: %(xpath)s"
                "Elements:%(tags)s"
                % {
                    "elements": len(tag_l),
                    "xpath": xpath,
                    "tags": tag_l,
                }
            )
        )

    return tag_l[0]


class CBL:
    _base_url = "https://clientes.cbl-logistica.com"

    def __init__(self, username, password, debug=False):
        self.session = requests.Session()
        self.viewstate = None
        self.username = username
        self.password = password
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/78.0.3904.108 Safari/537.36",
        }
        self.debug = debug

    def login(self):
        url = "%s/login.aspx" % self._base_url
        res = self.session.get(url, headers=self.headers)
        self._update_viewstate(res)
        # login
        form_data = {
            "ScriptManager1": "UpdatePanel1|Login1$LoginButton",
            "Login1$UserName": self.username,
            "Login1$Password": self.password,
            "Login1$LoginButton": "ENTRAR",
        }
        form_data.update(self.viewstate)
        res = self.session.post(url, data=form_data, headers=self.headers)
        self._update_viewstate(res)
        # Check login
        return not self.is_login_page(res)

    def filter_by_refcte(self, refcte):
        url = "%s/Consultas/envios.aspx" % self._base_url
        res = self.session.get(url, headers=self.headers)
        self._update_viewstate(res)

        userid_tags = [
            "ctl00_TOPCONTENEDOR_WebCUI_def_user",
            "ctl00_TOPCONTENEDOR_WebCUI_loginid",
            "ctl00_TOPCONTENEDOR_WebCUI_recid",
        ]

        tree = etree.HTML(res.text.encode())
        userid = None
        for ut in userid_tags:
            ut_tag = xpath1(tree, "//form[@id='aspnetForm']//input[@id='%s']" % ut)
            if ut_tag is None:
                raise ValidationError(_("Expected value"))
            if not userid:
                userid = ut_tag.attrib["value"]
            else:
                if userid != ut_tag.attrib["value"]:
                    raise ValidationError(_("Different userid values"))

        if not userid:
            raise ValidationError(_("Userid not found"))

        form_data = {
            "ctl00$AJAXScriptManager": "ctl00$UpdatePanel1|ctl00$TOPCONTENEDOR$WebCUI_buscar",
            "ctl00$TOPCONTENEDOR$WebCUI_del": "081",
            "ctl00$TOPCONTENEDOR$WebCUI_usuario": self.username,
            "ctl00$TOPCONTENEDOR$WebCUI_def_user": userid,
            "ctl00$TOPCONTENEDOR$WebCUI_loginid": userid,
            "ctl00$TOPCONTENEDOR$WebCUI_recid": userid,
            "ctl00$TOPCONTENEDOR$WebCUI_lista_f": "SAL",
            "ctl00$TOPCONTENEDOR$WebCUI_lista_sit": "TODO",
            "ctl00$TOPCONTENEDOR$WebCUI_ref": refcte,
            "ctl00$TOPCONTENEDOR$WebCUI_lista_tenv": "TODO",
            "ctl00$TOPCONTENEDOR$WebCUI_consulta": "1",
            "ctl00$TOPCONTENEDOR$WebCUI_delDest": "000",
            "ctl00$TOPCONTENEDOR$WebCUI_lista_grp": "TODOS",
            "ctl00$TOPCONTENEDOR$WebCUI_regxpag": "20",
            "ctl00$TOPCONTENEDOR$WebCUI_totalpag": "1",
            "ctl00$TOPCONTENEDOR$WebCUI_pers_cons": "S",
            "ctl00$TOPCONTENEDOR$WebCUI_sit_inc": "N",
            "ctl00$TOPCONTENEDOR$WebCUI_total_cons_gr1": "1",
            "ctl00$TOPCONTENEDOR$WebCUI_def_cons": "1",
            "ctl00$TOPCONTENEDOR$WebCUI_solocte": "S",
            "ctl00$TOPCONTENEDOR$WebCUI_diascons": "62",
            "ctl00$TOPCONTENEDOR$WebCUI_buscar": "Buscar",
        }
        form_data.update(self.viewstate)
        res = self.session.post(url, data=form_data, headers=self.headers)
        self._update_viewstate(res)

        # parse the page
        tree = etree.HTML(res.text.encode())
        elem_table_l = tree.xpath("//div[@id='CONSENV_RES']//table")
        if len(elem_table_l) == 0:
            return []
        elif len(elem_table_l) > 1:
            raise ValidationError(_("Unexpected content CONSENV_RES"))
        elem_table = elem_table_l[0]

        result_ld = []
        input_detail_l = elem_table.xpath(
            "//tr/td/input[contains(@onclick, 'MuestraDetalleConsulta')]"
        )
        for input_d in input_detail_l:
            m = re.match(
                r"^.+MuestraDetalleConsulta\('([^']+)'\)", input_d.attrib["onclick"]
            )
            if not m:
                raise ValidationError(_("Unexpected content on MuestraDetalleConsulta"))
            nexpedicion = m.group(1)

            # Expedition detail
            url = "%s/api/Comun/DetalleEnvio/QueryDatosExpedicion" % self._base_url
            form_data = {
                "expedicion": nexpedicion,
                "propietario": "null",
            }
            res = self.session.post(url, data=form_data, headers=self.headers)
            data = res.json()["data"]
            expedition_d = data

            # tracking
            url = "%s/api/Comun/DetalleEnvio/QueryTracking" % self._base_url
            form_data = {
                "jtStartIndex": "1",
                "jtPageSize": "1",
                "jtSorting": None,
                "expedicion": nexpedicion,
                "propietario": "null",
                "usuario": self.username,
            }
            res = self.session.post(url, data=form_data, headers=self.headers)
            data = json.loads(res.json()["data"])["Table"]
            for e in data:
                e["FECHA"] = datetime.datetime.strptime(e["FECHA"], "%Y-%m-%dT%H:%M:%S")
            expedition_d["Tracking"] = data

            result_ld.append(expedition_d)

        return result_ld

    def logout(self):
        url = "%s/Default.aspx" % self._base_url

        res = self.session.get(url, headers=self.headers)
        self._update_viewstate(res)

        form_data = {
            "__EVENTTARGET": "ctl00$LoginStatus1$ctl00",
            "__EVENTARGUMENT": "",
            "ctl00$jquerylang": "es",
            "ctl00$eschromeglobalactivo": "S",
            "ctl00$eschromebrowser": "S",
            "ctl00$chromeversion": "78",
            "ctl00$NoJavaPrint": "N",
        }
        form_data.update(self.viewstate)
        res = self.session.post(url, data=form_data, headers=self.headers)

        return self.is_login_page(res)

    def is_login_page(self, res):
        tree = etree.HTML(res.text.encode())
        tag_form_login = tree.xpath("//form[@id='frmlogin']")

        return len(tag_form_login) != 0

    def _update_viewstate(self, res):
        self.viewstate = {}
        tree = etree.HTML(res.text.encode())
        viewstate_fields = [
            "__VIEWSTATE",
            "__VIEWSTATEGENERATOR",
            "__VIEWSTATEENCRYPTED",
            "__EVENTVALIDATION",
        ]
        for vsf in viewstate_fields:
            tag_viewstate = tree.xpath("//*[@id='%s']" % vsf)
            for t in tag_viewstate:
                if "value" not in t.attrib:
                    raise ValidationError(
                        _(
                            "Unexpected, ViewState element iff found must have value attribute"
                        )
                    )
                if vsf not in self.viewstate:
                    self.viewstate[vsf] = t.attrib["value"] or None
                else:
                    if self.viewstate[vsf] != t.attrib["value"]:
                        raise ValidationError(
                            _(
                                "Unexpected! all the ViewState must have the same 'value'"
                            )
                        )

        if not self.viewstate:
            raise ValidationError(_("ViewState not found"))
