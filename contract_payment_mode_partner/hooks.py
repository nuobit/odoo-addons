# Copyright NuoBiT Solutions SL - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


def post_init_hook(env):
    env.cr.execute(
        """
        with partner_payment_mode as (
            select rp.id as partner_id, pm.id as payment_mode_id,
                   (
                     CASE WHEN f.name = 'supplier_payment_mode_id'
                     THEN 'purchase' else 'sale' end
                   ) as partner_type,
                   d.company_id
            from ir_default d, ir_model_fields f,
            res_partner rp, account_payment_mode pm
            where d.field_id = f.id and
                  f.ttype = 'many2one' and
                  f.name IN ('customer_payment_mode_id', 'supplier_payment_mode_id') and
                  d.user_id = rp.id and
                  d.json_value = 'account.payment.mode,' || pm.id
        )
        select c.id
        from contract_contract c, partner_payment_mode pm
        where c.partner_id = pm.partner_id and
              c.company_id = pm.company_id and
              c.contract_type = pm.partner_type AND
              c.payment_mode_id is distinct from pm.payment_mode_id
        """
    )
    contracts = env["contract.contract"].browse([row[0] for row in env.cr.fetchall()])
    contracts._compute_payment_mode_id()
