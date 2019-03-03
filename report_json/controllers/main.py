# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.web.controllers import main as report
from odoo.http import content_disposition, route, request

import json


class ReportController(report.ReportController):
    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == 'json':
            report = request.env['ir.actions.report']._get_report_from_name(
                reportname)
            context = dict(request.env.context)
            if docids:
                docids = [int(i) for i in docids.split(',')]
            if data.get('options'):
                data.update(json.loads(data.pop('options')))
            if data.get('context'):
                # Ignore 'lang' here, because the context in data is the one
                # from the webclient *but* if the user explicitely wants to
                # change the lang, this mechanism overwrites it.
                data['context'] = json.loads(data['context'])
                if data['context'].get('lang'):
                    del data['context']['lang']
                context.update(data['context'])
            json_data = report.with_context(context).render_json(
                docids, data=data
            )[0]
            jsonhttpheaders = [
                ('Content-Type', 'application/json'),
                ('Content-Length', len(json_data)),
                ('Content-Disposition', content_disposition(report.report_file + '.json')),
            ]
            return request.make_response(json_data, headers=jsonhttpheaders)
        return super(ReportController, self).report_routes(
            reportname, docids, converter, **data
        )
