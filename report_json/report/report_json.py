# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ReportJsonAbstract(models.AbstractModel):
    _name = "report.report_json.abstract"

    def _get_objs_for_report(self, docids, data):
        """
        Returns objects for json report.  From WebUI these
        are either as docids taken from context.active_ids or
        in the case of wizard are in data.  Manual calls may rely
        on regular context, setting docids, or setting data.

        :param docids: list of integers, typically provided by
            qwebactionmanager for regular Models.
        :param data: dictionary of data, if present typically provided
            by qwebactionmanager for TransientModels.
        :param ids: list of integers, provided by overrides.
        :return: recordset of active model for ids.
        """
        if docids:
            ids = docids
        elif data and "context" in data:
            ids = data["context"].get("active_ids", [])
        else:
            ids = self.env.context.get("active_ids", [])
        return self.env[self.env.context.get("active_model")].browse(ids)

    def create_json_report(self, docids, data):
        objs = self._get_objs_for_report(docids, data)
        json_data = self.generate_json_report(data, objs)
        return json_data, "json"

    def generate_json_report(self, data, objs):
        raise NotImplementedError()
