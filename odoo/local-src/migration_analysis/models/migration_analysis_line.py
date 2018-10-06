# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MigrationAnalysisLine(models.Model):
    _name = 'migration.analysis.line'
    _order = 'name'

    name = fields.Char(string='Module Name', required=True)

    description = fields.Char(
        string='Description', compute='_compute_description', store=True)

    analysis_id = fields.Many2one(
        comodel_name='migration.analysis', required=True, ondelete='cascade')

    line_serie_ids = fields.One2many(
        comodel_name='migration.analysis.line.serie',
        inverse_name='analysis_line_id')

    @api.depends('line_serie_ids.serie_id', 'line_serie_ids.state')
    def _compute_description(self):
        for line in self:
            line.description = '\n'.join([
                '%s-%s' % (x.owner_type, x.state)
                for x in line.line_serie_ids])
