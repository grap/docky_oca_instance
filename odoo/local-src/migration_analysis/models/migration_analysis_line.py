# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons.github_connector_oca.models.github_organization\
    import _OWNER_TYPE_SELECTION


class MigrationAnalysisLine(models.Model):
    _name = 'migration.analysis.line'
    _order = 'main_owner_type, name'

    name = fields.Char(string='Module Name', required=True)

    description = fields.Char(
        string='Description', compute='_compute_description', store=True)

    analysis_id = fields.Many2one(
        comodel_name='migration.analysis', required=True, ondelete='cascade')

    line_serie_ids = fields.One2many(
        comodel_name='migration.analysis.line.serie',
        inverse_name='analysis_line_id')

    main_owner_type = fields.Selection(
        selection=_OWNER_TYPE_SELECTION,
        compute='_compute_main_owner_type', store=True)

    @api.depends('line_serie_ids.serie_id', 'line_serie_ids.state')
    def _compute_description(self):
        for line in self:
            line.description = '\n'.join([
                '%s-%s' % (x.owner_type, x.state)
                for x in line.line_serie_ids])

    @api.depends('line_serie_ids.owner_type')
    def _compute_main_owner_type(self):
        for line in self:
            owner_types = line.mapped('line_serie_ids.owner_type')
            if '1_editor' in owner_types:
                line.main_owner_type = '1_editor'
            elif '2_oca' in owner_types:
                line.main_owner_type = '2_oca'
            elif '3_extra' in owner_types:
                line.main_owner_type = '3_extra'
            elif '4_custom' in owner_types:
                line.main_owner_type = '4_custom'
            else:
                line.main_owner_type = '5_undefined'
