# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from urllib.request import Request, urlopen

from odoo import api, fields, models
from odoo.addons.github_connector_oca.models.github_organization\
    import _OWNER_TYPE_SELECTION

_STATE_SELECTION = [
    ('ok_migration',        'OK (Migration Done)'),
    ('ok_new_module',       'OK (New Module)'),
    ('ok_removed_module',   'OK (Removed Module)'),
    ('ok_moved_module',     'OK (Moved Module)'),
    ('wip_migration',       'WIP (Migration)'),
    ('todo_migration',      'TODO (Migration)'),
]

class OdooMigrationLine(models.Model):
    _name = 'odoo.migration.line'

    migration_id = fields.Many2one(
        string='Odoo Migration', comodel_name='odoo.migration', required=True,
        ondelete='cascade')

    state = fields.Selection(
        name='Migration Status', selection=_STATE_SELECTION)

    module_name = fields.Char(
        string='Module Name', required=True)

    initial_owner_type = fields.Selection(
        selection=_OWNER_TYPE_SELECTION, string='Initial Owner Type')

    final_owner_type = fields.Selection(
        selection=_OWNER_TYPE_SELECTION, string='Final Owner Type')

    initial_serie_id = fields.Many2one(
        string='Initial Serie', comodel_name='github.serie',
        related='migration_id.initial_serie_id', store=True,
        ondelete='cascade')

    final_serie_id = fields.Many2one(
        string='Finale Serie', comodel_name='github.serie',
        related='migration_id.final_serie_id', store=True,
        ondelete='cascade')

    initial_module_version_id = fields.Many2one(
        string='Initial Module Version', comodel_name='odoo.module.version',
        ondelete='cascade')

    final_module_version_id = fields.Many2one(
        string='Finale Module Version', comodel_name='odoo.module.version',
        ondelete='cascade')

