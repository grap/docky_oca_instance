# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons.github_connector_oca.models.github_organization\
    import _OWNER_TYPE_SELECTION

from odoo.addons.migration_analysis.models.odoo_migration_line\
    import _STATE_SELECTION as _MIGRATION_STATE_SELECTION


class MigrationAnalysisLineSerie(models.Model):
    _name = 'migration.analysis.line.serie'

    _STATE_SELECTION = _MIGRATION_STATE_SELECTION + [
        ('initial', 'Initial'),
        ('unknown', 'Unknown'),
        ('ok_ported', 'OK (Ported Module)'),
        ('todo_port', 'TODO (Port)'),
    ]

    analysis_line_id = fields.Many2one(
        comodel_name='migration.analysis.line', required=True,
        ondelete='cascade')

    serie_id = fields.Many2one(comodel_name='github.serie')

    state = fields.Selection(
        string='State', selection=_STATE_SELECTION, default='unknown',
        required=True)

    owner_type = fields.Selection(
        string='Type', selection=_OWNER_TYPE_SELECTION, default='undefined',
        required=True)

    report_color = fields.Char(
        string='Color in the Report', compute='_compute_report_color')

    def _compute_report_color(self):
        for line_serie in self:
            if line_serie.state == 'initial' or 'ok_' in line_serie.state:
                line_serie.report_color = 'green'
            elif 'todo_' in line_serie.state:
                line_serie.report_color = 'orange'
            elif 'wip_' in line_serie.state:
                line_serie.report_color = 'yellow'
            else:
                line_serie.report_color = 'gray'
