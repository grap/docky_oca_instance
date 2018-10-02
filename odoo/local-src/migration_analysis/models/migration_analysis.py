# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MigrationAnalysis(models.Model):
    _name = 'migration.analysis'
    _order = 'name'

    name = fields.Char(string='Name', required=True)

    initial_serie_id = fields.Many2one(
        string='Initial Serie', comodel_name='github.serie', required=True)

    final_serie_id = fields.Many2one(
        string='Final Serie', comodel_name='github.serie', required=True)

    serie_ids = fields.Many2many(
        comodel_name='github.serie', compute='_compute_serie_ids', store=True)

    line_ids = fields.One2many(
        comodel_name='migration.analysis.line', inverse_name='analysis_id')

    @api.depends('initial_serie_id', 'final_serie_id')
    def _compute_serie_ids(self):
        for analysis in self:
            GithubSerie = self.env['github.serie']
            series = GithubSerie.search([
                ('sequence', '>=', analysis.initial_serie_id.sequence),
                ('sequence', '<=', analysis.final_serie_id.sequence),
                ])
            analysis.serie_ids = series.ids

    def button_analyse(self):
        for analysis in self:
            analysis._clear_analysis()
            analysis._do_analysis()

    def _clear_analysis(self):
        self.mapped('line_ids.line_serie_ids').unlink()

    def _do_analysis(self):
        self.ensure_one()
        AnalysisLineSerie = self.env['migration.analysis.line.serie']
        for serie in self.serie_ids:
            for line in self.line_ids:
                new_line_serie = AnalysisLineSerie.create({
                    'analysis_line_id': line.id,
                    'serie_id': serie.id,
                })
