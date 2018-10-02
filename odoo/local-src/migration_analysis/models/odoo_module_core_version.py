# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class OdooModuleCoreVersion(models.Model):
    _name = 'odoo.module.core.version'

    _NEXT_VERSION_STATE = [
        ('ok', 'OK'),
        ('wip', 'Work In Progress'),
        ('to_migrate', 'To Migrate'),
        
    ]

    serie_id = fields.Many2one(
        string='Serie', comodel_name='github.serie', required=True)

    module_id = fields.Many2one(
        comodel_name='odoo.module', string='Odoo Core Module', required=True)

    next_version_state = fields.Selection(
        selection=_NEXT_VERSION_STATE, string='Next Version State')

    # Custom Section
    @api.model
    def create_if_not_exist(self, module, serie):
        core_version = self.search([
            ('module_id', '=', module.id),
            ('serie_id', '=', serie.id),
        ])
        if not core_version:
            core_version = self.create({
                'module_id': module.id,
                'serie_id': serie.id,
            })
        return core_version
