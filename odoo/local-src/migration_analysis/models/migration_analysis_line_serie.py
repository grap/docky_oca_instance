# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MigrationAnalysisLineSerie(models.Model):
    _name = 'migration.analysis.line.serie'

    analysis_line_id = fields.Many2one(
        comodel_name='migration.analysis.line', required=True,
        ondelete='cascade')

    serie_id = fields.Many2one(comodel_name='github.serie')
