# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class LightingProductAdapter(Component):
    _name = 'sapb1.lighting.product.adapter'
    _inherit = 'sapb1.adapter'

    _apply_on = 'sapb1.lighting.product'

    _sql_search = r""""""

    _sql_read = r"""WITH product0 AS (
                        SELECT p."ItemCode", p."ItemName", p."CodeBars", p."AvgPrice", 
                               p."ItmsGrpCod", p."U_U_familia", p."U_U_aplicacion",
                               p."U_ACC_Obsmark",
                               to_varchar(COALESCE(to_date(p."UpdateDate"), TO_DATE('1900-12-31', 
                                                   'YYYY-MM-DD'))) AS "UpdateDate_str",
                               COALESCE(REPLACE_REGEXPR('([0-9]{2})([0-9]{2})([0-9]{2})' 
                                                        IN lpad(to_varchar(p."UpdateTS"), 6, '0')
                                                        WITH '\1:\2:\3'), '00:00:00') AS "UpdateTS_str"                                             
                        FROM %(schema)s.OITM p
                        WHERE p."ItemCode" NOT LIKE_REGEXPR '^.+\..+$'
                    ),
                    product1 AS (
                        SELECT p."ItemCode", p."ItemName", p."CodeBars", p."AvgPrice",
                               g."ItmsGrpNam", p."U_U_familia", p."U_U_aplicacion",
                               p."U_ACC_Obsmark", 
                               to_timestamp(concat(p."UpdateDate_str", concat(' ', p."UpdateTS_str")), 
                                           'YYYY-MM-DD HH24:MI:SS') AS "UpdateDateTime"
                        FROM product0 p, %(schema)s.OITB g
                        WHERE p."ItmsGrpCod" = g."ItmsGrpCod" 
                    ),
                    stock AS (
		   	            SELECT pw."ItemCode",
		  	                   pw."OnHand" - pw."IsCommited" AS "Available",
			                   pw."updateDate" 
			            FROM %(schema)s.OITW pw
			            WHERE pw."WhsCode" = '00'
                    ),
                    product as (
                        SELECT p."ItemCode", p."ItemName", p."CodeBars", p."AvgPrice",
                               p."ItmsGrpNam", p."U_U_familia", p."U_U_aplicacion",
                               p."U_ACC_Obsmark", 
                               (CASE WHEN s."Available" < 0 THEN 0 ELSE s."Available" END) AS "Available",
                               (CASE WHEN SECONDS_BETWEEN(s."updateDate", p."UpdateDateTime") > 0 THEN p."UpdateDateTime"
                                ELSE s."updateDate" END) AS "UpdateDateTime"
                        FROM product1 p, stock s
                        WHERE p."ItemCode" = s."ItemCode" and
                              p."U_ACC_Obsmark" IN ('Novedades', 'Catalogado', 'Descatalogado', 
                                                   'Fe Digital', 'Histórico', 'Especiales') and
                              p."ItmsGrpNam" in ('Cristher', 'Dopo', 'Exo', 'Indeluz', 'Accesorios')
                    )
                    select %(fields)s
                    from product
                    %(where)s
                 """

    _id = ('ItemCode',)
