# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    ### remove model and dependencies
    model_name = 'lighting.product.source.line.marketingwattage'

    MODULE_UNINSTALL_FLAG = '_force_unlink'
    context_flags = {
        MODULE_UNINSTALL_FLAG: True,
    }

    ## get model id
    env.cr.execute(
        "SELECT id from ir_model WHERE model = %s",
        (model_name,))
    row = env.cr.fetchone()
    if not row:
        return
    model_id, = row

    # attachments
    attachments = env['ir.attachment'].search([
        ('res_model', '=', model_name)
    ])
    if attachments:
        env.cr.execute(
            "UPDATE ir_attachment SET res_model = NULL "
            "WHERE id in %s",
            (tuple(attachments.ids), ))

    # constraints
    env['ir.model.constraint'].search([
        ('model', '=', model_id),
    ]).unlink()

    # fields related
    relations = env['ir.model.fields'].search([
        ('relation', '=', model_name),
    ]).with_context(**context_flags)
    for relation in relations:
        try:
            # Fails if the model on the target side
            # cannot be instantiated
            relation.unlink()
        except KeyError:
            pass
        except AttributeError:
            pass

    # relations
    env['ir.model.relation'].search([
        ('model', '=', model_id)
    ]).with_context(**context_flags).unlink()

    # model itself
    env['ir.model'].browse([model_id]).with_context(**context_flags).unlink()

    ### remove table
    env.cr.execute(
        "DROP TABLE lighting_product_source_line_marketingwattage"
    )