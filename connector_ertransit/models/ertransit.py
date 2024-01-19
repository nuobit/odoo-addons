# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import datetime
import decimal
import logging

import requests
from lxml import etree

_logger = logging.getLogger(__name__)


def xpath1(tree, xpath):
    tag_l = tree.xpath(xpath)
    if len(tag_l) != 1:
        raise Exception("Expected 1 element")

    return tag_l[0]


def trim_d(d):
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, str):
                d[k] = v.strip() or None
            elif isinstance(v, (int, datetime.datetime, decimal.Decimal)):
                pass
            elif v is None:
                pass
            elif isinstance(v, (dict, list)):
                trim_d(v)
            else:
                raise Exception("no tractat 2!! %s:%s -> %s" % (k, v, type(v)))
    elif isinstance(d, list):
        for d_d in d:
            trim_d(d_d)
    else:
        raise Exception("no tractat 1!! %s -> %s" % (d, type(d)))


class ERTransit:
    def __init__(self, username, password, debug=False):
        self.session = requests.Session()
        self.javax_face_viewstate = None
        self.debug = debug
        self.username = username
        self.password = password

    def login(self):
        url = "https://b2b.ertransit.com/portal/transkalweb/login.xhtml"

        ## obtenim el javax.faces
        res = self.session.get(url, params={"loc": "es"})
        self._update_javax_faces_viewstate(res)

        ## fem el login
        data = {
            "frmLogin": "frmLogin",
            "frmLogin:txtUsuarioTranskal": self.username,
            "frmLogin:j_idt131": self.password,
            "frmLogin:j_idt135": "es_ES",
            "frmLogin:btnLogin": "Entrar",
            "javax.faces.ViewState": self.javax_face_viewstate,
        }
        res = self.session.post(url, data=data)
        self._update_javax_faces_viewstate(res)

        return not self.is_login_page(res)

    def filter_by_reffra(self, reffra):
        url = "https://b2b.ertransit.com/portal/transkalweb/listaNotaCarga.xhtml"
        data = {
            "formFiltro": "formFiltro",
            "formFiltro:filtroNombreCliente": "52974",
            "formFiltro:filtroTipoServicio": None,
            "formFiltro:filtroEstado": None,
            "formFiltro:filtroParam0": None,
            "formFiltro:filtroParam2": None,
            "formFiltro:filtroParam4": None,
            "formFiltro:filtroParam6": None,
            "formFiltro:filtroDesdeFechaCarga": None,
            "formFiltro:filtroHastaFechaCarga": None,
            "formFiltro:filtroDesdeFechaDescarga": None,
            "formFiltro:filtroHastaFechaDescarga": None,
            "formFiltro:filtroParam1": None,
            "formFiltro:filtroParam3": None,
            "formFiltro:filtroParam5": reffra,
            "formFiltro:j_idt226": "Filtrar",
            "javax.faces.ViewState": self.javax_face_viewstate,
        }
        res = self.session.post(url, data=data)
        self._update_javax_faces_viewstate(res)

        tree = etree.HTML(res.text.encode())
        elem_table = xpath1(tree, "//table[@id='tablaResultados']")

        elem_header = xpath1(elem_table, "tbody/tr[@class='row1']")
        header_l = [x.strip() for x in elem_header.xpath("td/text()")]

        result_ld = []
        elem_rows = elem_table.xpath("tbody/tr[starts-with(@id,'row_')]")
        for e_row in elem_rows:
            row_d = dict(
                zip(
                    header_l,
                    [x.text and x.text.strip() or None for x in e_row.xpath("td")],
                )
            )
            trim_d(row_d)
            result_ld.append(row_d)

        return result_ld

    def logout(self):
        url = "https://b2b.ertransit.com/portal/transkalweb/listaNotaCarga.xhtml"

        data = {
            "j_idt98": "j_idt98",
            "javax.faces.ViewState": self.javax_face_viewstate,
            "j_idt98:j_idt100": "j_idt98:j_idt100",
        }

        res = self.session.post(url, data=data)
        self._update_javax_faces_viewstate(res)

        return self.is_login_page(res)

    #### private

    def _log(self, filename, res):
        if self.debug:
            with open(filename, "w") as f:
                f.write(res.text)

    def is_login_page(self, res):
        tree = etree.HTML(res.text.encode())
        tag_form_login = tree.xpath("//form[@id='frmLogin']")

        return len(tag_form_login) != 0

    def _update_javax_faces_viewstate(self, res):
        self.javax_face_viewstate = None
        tree = etree.HTML(res.text.encode())
        tag_javax = tree.xpath('//*[@id="javax.faces.ViewState"]')
        for t in tag_javax:
            if "value" not in t.attrib:
                raise Exception(
                    "Unexpected, the javax.faces.ViewState element if found must have value attribute"
                )
            if not self.javax_face_viewstate:
                self.javax_face_viewstate = t.attrib["value"]
            else:
                if self.javax_face_viewstate != t.attrib["value"]:
                    raise Exception(
                        "Unexpected! all the javax.faces.ViewState must have the same 'value'"
                    )

        if not self.javax_face_viewstate:
            raise Exception("javax.faces.ViewState not found")
