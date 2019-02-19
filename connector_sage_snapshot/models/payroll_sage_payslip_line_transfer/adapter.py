# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component

import sqlite3

import logging

import datetime

_logger = logging.getLogger(__name__)


class PayslipLineTransferAdapter(Component):
    _inherit = 'sage.payroll.sage.payslip.line.transfer.adapter'

    def _exec_query(self, filters=None, fields=None, as_dict=True):
        snapshot_ids = self.env['connector.sage.snapshot.database'].search([
            ('company_id', '=', self.backend_record.company_id.id),
            ('year', '=', filters.get('Año')),
            ('month', '=', filters.get('MesD')),
        ])
        if snapshot_ids:
            attachment_id = self.env['ir.attachment'].search([
                ('id', '!=', False),
                ('res_id', '=', snapshot_ids.id),
                ('res_model', '=', snapshot_ids._name),
                ('res_field', '=', 'datas'),
            ])
            dbfile = attachment_id._full_path(attachment_id.store_fname)

            conn = sqlite3.connect(dbfile)

            c = conn.cursor()

            sql = """select n.CodigoEmpresa, n.Año, n.MesD, 
                            n.CodigoEmpleado, n.CodigoConceptoNom, 
                            c.CodigoConvenio, c.FechaRegistroCV,  
                            n.FechaCobro,
                            min(n.ConceptoLargo) as ConceptoLargo,
                            sum(n.ImporteNom) as ImporteNom
                     from Historico n, ConvenioConcepto c
                     where n.TotalFichaHistorica in ('TD1', 'TR1') AND
                           n.CodigoConceptoNom = c.CodigoConceptoNom AND
                           n.CodigoEmpresa = c.CodigoEmpresa AND
                           n.CodigoEmpresa = :CodigoEmpresa AND
                           n.Año = :Año AND
                           n.MesD = :MesD AND
                           n.FechaCobro = :FechaCobro AND
                           (:CodigoEmpleado is null or n.CodigoEmpleado = :CodigoEmpleado) AND
                           (:CodigoConceptoNom is null or n.CodigoConceptoNom = :CodigoConceptoNom) AND
                           c.CodigoConvenio = :CodigoConvenio AND
                           c.FechaRegistroCV = :FechaRegistroCV
                     group by n.CodigoEmpresa, n.Año, n.MesD, 
                              n.CodigoEmpleado, n.CodigoConceptoNom, 
                              c.CodigoConvenio, c.FechaRegistroCV,  
                              n.FechaCobro
                     having sum(n.importenom) != 0
            """

            datetime_fields = set()
            params_d = {}
            for p in self._id:
                if p in filters:
                    v = filters[p]
                    if isinstance(v, (datetime.date, datetime.datetime)):
                        datetime_fields.add(p)
                        v = v.strftime('%Y-%m-%d %H:%M:%S')
                    params_d[p] = v
                else:
                    params_d[p] = None

            c.execute(sql, params_d)

            res = []
            headers = [desc[0] for desc in c.description]
            for row in c:
                row_d = dict(zip(headers, row))
                for f in datetime_fields:
                    if f in row_d:
                        row_d[f] = datetime.datetime.strptime(row_d[f], '%Y-%m-%d %H:%M:%S')
                for f in filters:
                    if f not in row_d:
                        row_d[f] = filters[f]
                res.append(row_d)

            c.close()
            conn.close()

            ### cmprovem que la clau primaria sigui unica
            if self._id and set(self._id).issubset(set(filters)):
                self._check_uniq(res)

            return res
        else:
            return super()._exec_query(filters=filters, fields=fields, as_dict=as_dict)
