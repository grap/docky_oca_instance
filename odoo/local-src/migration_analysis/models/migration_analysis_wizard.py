# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MigrationAnalysisWizard(models.Model):
    _name = 'migration.analysis.wizard'

    migration_analysis_id = fields.Many2one(
        string='Migration Analysis', comodel_name='migration.analysis',
        required=True, readonly=True)

    module_list = fields.Text(string='Module List', required=True)

    def button_update_module_list(self):
        self.ensure_one()
        MigrationAnalysisLine = self.env['migration.analysis.line']
        module_list = [
            x.strip() for x in self.module_list.replace('\n', ' ').split(' ')
            if x.strip()]
        current_list = self.mapped('migration_analysis_id.line_ids.name')
        for module_name in module_list:
            if module_name not in current_list:
                MigrationAnalysisLine.create({
                    'analysis_id': self.migration_analysis_id.id,
                    'name': module_name,
                })
