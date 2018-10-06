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
        AnalysisLineSerie = self.env['migration.analysis.line.serie']
        OdooModuleCoreVersion = self.env['odoo.module.core.version']
        previous_serie = False
        for serie in self.serie_ids:
            for line in self.line_ids:
                state = 'unknown'
                type = 'custom'

                # Identify module position (type)
                module_core_version = OdooModuleCoreVersion.search([
                    ('serie_id', '=', serie.id),
                    ('module_name', '=', line.name),
                ])
                if module_core_version:
                    type = 'odoo'
                else:
                    pass
#                    oca_module_version = OdooModuleVersion.search([
#                    ])

                # Identify workload (state)
                if not previous_serie:
                    # First Version
                    state = 'initial'

                else:
                    # Upgrade Version
                    # Try to get previous module serie
                    previous_module_core_version =\
                        OdooModuleCoreVersion.search([
                            ('serie_id', '=', previous_serie.id),
                            ('module_name', '=', line.name),
                        ])
                    if previous_module_core_version:
                        state =\
                            previous_module_core_version.next_version_state
                        if not state:
                            # TODO, understand weird case
                            state = 'unknown'
                new_line_serie = AnalysisLineSerie.create({
                    'type': type,
                    'state': state,
                    'analysis_line_id': line.id,
                    'serie_id': serie.id,
                })
            previous_serie = serie
