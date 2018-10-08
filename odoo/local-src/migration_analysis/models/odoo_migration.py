# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from urllib.request import Request, urlopen

from odoo import _, api, exceptions, fields, models


class OdooMigration(models.Model):
    _name = 'odoo.migration'
    _order = 'initial_serie_id'

    _BEGIN_TABLE_PARSE_VALUES = [
        "+===================================+===================================+\n",
        "+========================================+==========================================+\n",
        "+===================================+=================================================+\n",
        "+============================================+=================================================+\n",
    ]
    _LINE_SPLIT_PARSE_VALUES = [
        "+-----------------------------------+-----------------------------------+\n",
        "+----------------------------------------+------------------------------------------+\n",
        "+-----------------------------------+-------------------------------------------------+\n",
        "+--------------------------------------------+-------------------------------------------------+\n",
    ]

    _mapping_analysis = {
        'Done': 'ok_migration',
        'No change': 'ok_migration',
        'Nothing to do': 'ok_migration',
        'work in progress': 'wip_migration',
        'Moved to OCA': 'ok_migration',
    }

    initial_serie_id = fields.Many2one(
        string='Initial Serie', comodel_name='github.serie', required=True,
        domain="[('type', '=', 'odoo')]")

    final_serie_id = fields.Many2one(
        string='Final Serie', comodel_name='github.serie', required=True,
        domain="[('type', '=', 'odoo')]")

    odoo_coverage_url = fields.Char(
        string='URL of the Coverage file',
        help="Usually set in the OpenUpgrade Project")

    line_ids = fields.One2many(
        string='Migration Lines', comodel_name='odoo.migration.line',
        inverse_name='migration_id')

    coverage_percent = fields.Float(
        digits=(6, 2), string='Coverage (%)',
        readonly=True)

    def button_analyse_coverage(self):
        OdooModule = self.env['odoo.module']
        OodooModuleVersion = self.env['odoo.module.version']
        OdooMigrationLine = self.env['odoo.migration.line']
        for migration in self:
            migration.line_ids.unlink()
            data_list = self._parse_openupgrade_file()
            for item in data_list:
                migration_state = 'todo_migration'
                if '|new|' in item:
                    item = item.replace('|new|', '')
                if '|del|' in item:
                    item = item.replace('|del|', '')
                module_data = item.replace("\n", "").split("|")
                module_data = [
                    x.strip() for x in module_data if x not in ['', ', ']]
                if len(module_data) >= 2:
                    # Parse Data
                    module_name = module_data[0]
                    # TODO, analyse if module has been renamed. (Is it possible ?)
                    new_module_name = module_name
                    initial_versions = OodooModuleVersion.search([
                        ('technical_name', '=', module_name),
                        ('serie_id', '=', migration.initial_serie_id.id),
                    ])

                    # Try to get initial and final module versions
                    if len(initial_versions) > 1:
                        exceptions.Warning(_(
                            "Many Module Version found for the module %s"
                            ", version %s" % (
                                module_name, migration.initial_serie_id.name)))
                    final_versions = OodooModuleVersion.search([
                        ('technical_name', '=', new_module_name),
                        ('serie_id', '=', migration.final_serie_id.id),
                    ])
                    if len(final_versions) > 1:
                        exceptions.Warning(_(
                            "Many Module Version found for the module %s"
                            ", version %s" % (
                                new_module_name,
                                migration.initial_serie_id.name)))

                    if initial_versions:
                        initial_version_id = initial_versions[0].id
                        initial_owner_type = initial_versions[0].owner_type
                    else:
                        initial_version_id = False
                        initial_owner_type = '5_undefined'

                    if final_versions:
                        final_version_id = final_versions[0].id
                        final_owner_type = final_versions[0].owner_type
                    else:
                        final_version_id = False
                        final_owner_type = '5_undefined'

                    # Analyse state (1/2 : Simple Cases)
                    if not initial_versions:
                        # New module --> Always OK
                        migration_state = 'ok_new_module'
                    elif not final_versions:
                        # Removed module --> We assume it's always OK,
                        # because we don't have any way to know it
                        migration_state = 'ok_removed_module'
                    else:
                        if final_owner_type != '1_editor':
                            migration_state = 'ok_moved_module'

                    # Analyse state (2/2 : Parsing document)
                    if migration_state == 'todo_migration':
                        migration_state_text = module_data[1]
                        for k, v in self._mapping_analysis.items():
                            if k in migration_state_text:
                                migration_state = v

                    # Creation migration lines
                    OdooMigrationLine.create({
                        'migration_id': migration.id,
                        'state': migration_state,
                        'module_name': module_name,
                        'initial_module_version_id': initial_version_id,
                        'initial_owner_type': initial_owner_type,
                        'final_module_version_id': final_version_id,
                        'final_owner_type': final_owner_type,
                    })
            ok_lines = migration.line_ids.filtered(
                lambda x: x.state in [
                    'ok_migration', 'ok_new_module', 'ok_removed_module',
                    'ok_moved_module'])
            
            migration.coverage_percent =\
                len(ok_lines) / len(migration.line_ids) * 100

    def _parse_openupgrade_file(self):
        self.ensure_one()
        table_data = ""
        data = urlopen(Request(self.odoo_coverage_url)).read().decode('utf-8')
        for parse_value in self._BEGIN_TABLE_PARSE_VALUES:
            if parse_value in data:
                table_data = data.split(parse_value)[1]
        data_list = []
        for parse_value in self._LINE_SPLIT_PARSE_VALUES:
            if parse_value in table_data:
                data_list = table_data.split(parse_value)
        return data_list
