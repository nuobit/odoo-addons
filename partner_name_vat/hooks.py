# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


def post_init_hook_vat_update(env):
    env["res.partner"].with_context(active_test=False).search(
        []
    )._compute_display_name()


def uninstall_hook_vat_remove(env):
    env["res.partner"].with_context(active_test=False).search(
        []
    )._compute_display_name()
