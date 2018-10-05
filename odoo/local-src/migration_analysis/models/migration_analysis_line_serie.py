# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MigrationAnalysisLineSerie(models.Model):
    _name = 'migration.analysis.line.serie'

    _STATE_SELECTION = [
        ('unknown', 'Unknown'),
        ('initial', 'Initial'),
        ('ok', 'OK'),
        ('to_migrate', 'To Migrate'),
        ('obsolete', 'Obsolete'),
    ]

    _TYPE_SELECTION = [
        ('odoo', 'Odoo'),
        ('OCA', 'OCA'),
        ('custom', 'Custom'),
    ]

    analysis_line_id = fields.Many2one(
        comodel_name='migration.analysis.line', required=True,
        ondelete='cascade')

    serie_id = fields.Many2one(comodel_name='github.serie')

    state = fields.Selection(
        string='State', selection=_STATE_SELECTION, default='unknown',
        required=True)

    type = fields.Selection(
        string='Type', selection=_TYPE_SELECTION, default='custom',
        required=True)