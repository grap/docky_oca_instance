# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MigrationAnalysis(models.Model):
    _name = 'migration.analysis'
    _order = 'name'

    # Default Section
    def _default_user_id(self):
        return self.env.user.company_id

    # Fields Section
    name = fields.Char(string='Name', required=True)

    user_id = fields.Many2one(
        comodel_name='res.users', required=True, default=_default_user_id)

    initial_serie_id = fields.Many2one(
        string='Initial Serie', comodel_name='github.serie', required=True)

    final_serie_id = fields.Many2one(
        string='Final Serie', comodel_name='github.serie', required=True)

    serie_ids = fields.Many2many(
        comodel_name='github.serie', compute='_compute_serie_ids', store=True)

    line_ids = fields.One2many(
        comodel_name='migration.analysis.line', inverse_name='analysis_id')

    # Compute Section
    @api.depends('initial_serie_id', 'final_serie_id')
    def _compute_serie_ids(self):
        for analysis in self:
            GithubSerie = self.env['github.serie']
            series = GithubSerie.search([
                ('sequence', '>=', analysis.initial_serie_id.sequence),
                ('sequence', '<=', analysis.final_serie_id.sequence),
                ])
            analysis.serie_ids = series.ids

    # View Section
    def button_analyse(self):
        for analysis in self:
            analysis._clear_analysis()
            analysis._do_analysis()

    # Custom Section
    def _clear_analysis(self):
        self.mapped('line_ids.line_serie_ids').unlink()

    def _do_analysis(self):
        self.ensure_one()
        OdooModuleVersion = self.env['odoo.module.version']
        MigrationLine = self.env['odoo.migration.line']
        AnalysisLineSerie = self.env['migration.analysis.line.serie']
        previous_serie = False
        for serie in self.serie_ids:
            previous_line_serie = False
            for line in self.line_ids:
                state = 'unknown'

                # Find the OpenUpgrade migration result (if any)
                migration_line = MigrationLine.search([
                    ('module_name', '=', line.name),
                    ('initial_serie_id', '=', serie.id),
                ])

                # Find Odoo Module Version (if found)
                if previous_serie:
                    previous_module_version = OdooModuleVersion.search([
                        ('technical_name', '=', line.name),
                        ('serie_id', '=', previous_serie.id),
                    ])
                current_module_version = OdooModuleVersion.search([
                    ('technical_name', '=', line.name),
                    ('serie_id', '=', serie.id),
                ])

                # Define owner type
                if current_module_version:
                    owner_type = current_module_version.owner_type
                else:
                    owner_type = 'undefined'

                # Identify workload (state)
                if not previous_serie:
                    # First Version
                    state = 'initial'
                elif migration_line:
                    state = migration_line.state
                elif previous_module_version:
                    if current_module_version and previous_module_version.owner_type != 'editor':
                        state = 'ok_ported'
                    elif previous_line_serie.state == 'ok_removed_module':
                        state = 'ok_removed_module'
                    else:
                        state = 'todo_port'
                else:
                    if current_module_version:
                        state = 'ok_ported'
                    else:
                        state = 'unknown'

                new_line_serie = AnalysisLineSerie.create({
                    'owner_type': owner_type,
                    'state': state,
                    'analysis_line_id': line.id,
                    'serie_id': serie.id,
                })
                previous_line_serie = new_line_serie
            previous_serie = serie
