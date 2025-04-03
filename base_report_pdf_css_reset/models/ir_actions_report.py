# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import lxml.html
from markupsafe import Markup

from odoo import models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _prepare_html(self, html, report_model=False):
        (
            bodies,
            res_ids,
            header,
            footer,
            specific_paperformat_args,
        ) = super()._prepare_html(html, report_model=report_model)
        if self.env.context.get("no_paddings", False):
            bodies_tmp = []
            for body in bodies:
                root = lxml.html.fromstring(body)
                body_class = root.xpath("body[@class]")
                if body_class:
                    elem = body_class[0]
                    classes_tmp = []
                    for klass in elem.attrib["class"].split(" "):
                        if klass != "container":
                            classes_tmp.append(klass)
                    if not classes_tmp:
                        del elem.attrib["class"]
                    else:
                        elem.attrib["class"] = " ".join(classes_tmp)
                    bodies_tmp.append(Markup(lxml.html.tostring(root).decode()))
            bodies = bodies_tmp
        return bodies, res_ids, header, footer, specific_paperformat_args
