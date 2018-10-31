# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from urllib.request import Request, urlopen

from odoo import _, api, exceptions, fields, models


class OdooMigration(models.Model):
    _name = 'odoo.migration'
    _order = 'initial_serie_id'

    _BEGIN_TABLE_PARSE_VALUES = [
        "+===================================+================================"
        "===+\n",
        "+========================================+==========================="
        "===============+\n",
        "+===================================+================================"
        "=================+\n",
        "+============================================+======================="
        "==========================+\n",
    ]
    _LINE_SPLIT_PARSE_VALUES = [
        "+-----------------------------------+--------------------------------"
        "---+\n",
        "+----------------------------------------+---------------------------"
        "---------------+\n",
        "+-----------------------------------+--------------------------------"
        "-----------------+\n",
        "+--------------------------------------------+-----------------------"
        "--------------------------+\n",
    ]

    _MAPPING_ANALYSIS = {
        'Done': 'ok_migration',
        'No change': 'ok_migration',
        'Nothing to do': 'ok_migration',
        'work in progress': 'wip_migration',
        'Moved to OCA': 'ok_migration',
    }

    name = fields.Char(compute='_compute_name', store=True)

    initial_serie_id = fields.Many2one(
        string='Initial Serie', comodel_name='github.serie', required=True,
        domain="[('type', '=', 'odoo')]")

    final_serie_id = fields.Many2one(
        string='Final Serie', comodel_name='github.serie', required=True,
        domain="[('type', '=', 'odoo')]")

    openupgrade_coverage_url = fields.Char(
        oldname='odoo_coverage_url',
        string='URL of the Coverage file',
        help="Usually set in the OpenUpgrade Project")

    openupgrade_module_url = fields.Char(
        oldname='odoo_merged_module_url',
        string='URL of the Modules file',
        help="Usually set in the OpenUpgrade Project, in a apriori.py file")

    coverage_text = fields.Text(readonly=True)
    renamed_module_text = fields.Text(readonly=True)
    merged_module_text = fields.Text(readonly=True)

    line_ids = fields.One2many(
        string='Migration Lines', comodel_name='odoo.migration.line',
        inverse_name='migration_id')

    line_qty = fields.Integer(
        string="Line Quantity", compute='_compute_line_qty')

    coverage_percent = fields.Float(
        digits=(6, 2), string='Coverage (%)',
        readonly=True)

    # _TEST_MODULE = [
    #     'base',                 # ok_migration
    #     'point_of_sale',        # todo_migration
    #     'account',              # ok_migration
    #     'account_chart',        # ok_migration. KO Should be merged
    #     'edi',
    #     'knowledge',
    #     'disable_openerp_online',
    # ]
    # _TEST_MODULE = []

    @api.depends('line_ids')
    def _compute_line_qty(self):
        for migration in self:
            migration.line_qty = len(migration.line_ids)

    @api.depends('initial_serie_id', 'final_serie_id')
    def _compute_name(self):
        for migration in self:
            migration.name = _("Migration from %s to %s") % (
                migration.initial_serie_id.name,
                migration.final_serie_id.name)

    def button_analyse_coverage(self):
        self.ensure_one()
        OdooMigrationLine = self.env['odoo.migration.line']
        self.line_ids.unlink()
        self._parse_openupgrade_coverage_file()
        self._parse_openupgrade_module_file()

        coverage_modules = eval(self.coverage_text)
        renamed_modules = self.renamed_module_text\
            and eval(self.renamed_module_text) or {}
        merged_modules = self.merged_module_text\
            and eval(self.merged_module_text) or {}

        # Analyse
        for module_name, coverage_state in coverage_modules.items():
            migration_state = 'todo_migration'
            # if module_name not in self._TEST_MODULE:
            #     continue
            new_module_name, name_state, initial_version, final_version =\
                self._get_versions(
                    module_name, renamed_modules, merged_modules)

            if initial_version:
                initial_version_id = initial_version.id
                initial_owner_type = initial_version.owner_type
            else:
                initial_version_id = False
                initial_owner_type = '5_undefined'

            if final_version:
                final_version_id = final_version.id
                final_owner_type = final_version.owner_type
            else:
                final_version_id = False
                final_owner_type = '5_undefined'

            # Analyse state (1/2 : Simple Cases)
            if not initial_version:
                # New module --> Always OK
                migration_state = 'ok_new_module'
            elif not final_version:
                # todo_port
                migration_state = 'todo_port_module'
            else:
                if final_owner_type != '1_editor':
                    migration_state = 'ok_moved_module'

            # Analyse state (2/2 : Parsing document)
            if migration_state == 'todo_migration':
                migration_state = coverage_state

            # Creation migration lines
            OdooMigrationLine.create({
                'migration_id': self.id,
                'state': migration_state,
                'name_state': name_state,
                'module_name': module_name,
                'new_module_name': new_module_name,
                'initial_module_version_id': initial_version_id,
                'initial_owner_type': initial_owner_type,
                'final_module_version_id': final_version_id,
                'final_owner_type': final_owner_type,
            })

        # Compute coverage percentage
        ok_lines = self.line_ids.filtered(
            lambda x: x.state in [
                'ok_migration', 'ok_new_module', 'ok_removed_module',
                'ok_moved_module'])

        self.coverage_percent = self.line_ids and (
            len(ok_lines) / len(self.line_ids) * 100) or 0

        # Handle renamed modules that are not in Odoo Core
        for module_name, coverage_state in renamed_modules.items():
            if module_name in coverage_modules:
                continue
            new_module_name, name_state, initial_version, final_version =\
                self._get_versions(
                    module_name, renamed_modules, merged_modules)

            if final_version:
                migration_state = 'ok_ported_module'

            # Creation migration lines
            OdooMigrationLine.create({
                'migration_id': self.id,
                'state':
                final_version and 'ok_ported_module' or 'todo_port_module',
                'name_state': 'renamed',
                'module_name': module_name,
                'new_module_name': new_module_name,
                'initial_module_version_id': initial_version.id,
                'initial_owner_type': initial_version.owner_type,
                'final_module_version_id': final_version and final_version.id,
                'final_owner_type':
                final_version and final_version.owner_type or '5_undefined',
            })

        # Handle merged modules that are not in Odoo Core
        for module_name, coverage_state in merged_modules.items():
            if module_name in coverage_modules:
                continue
            new_module_name, name_state, initial_version, final_version =\
                self._get_versions(
                    module_name, renamed_modules, merged_modules)

            if final_version:
                migration_state = 'ok_ported_module'

            # Creation migration lines
            OdooMigrationLine.create({
                'migration_id': self.id,
                'state':
                final_version and 'ok_ported_module' or 'todo_port_module',
                'name_state': 'merged',
                'module_name': module_name,
                'new_module_name': new_module_name,
                'initial_module_version_id': initial_version.id,
                'initial_owner_type': initial_version.owner_type,
                'final_module_version_id': final_version and final_version.id,
                'final_owner_type':
                final_version and final_version.owner_type or '5_undefined',
            })

        # Handle merged modules that are not in the Odoo Core

    def _get_versions(self, module_name, renamed_modules, merged_modules):
        OodooModuleVersion = self.env['odoo.module.version']

        if module_name in renamed_modules:
            name_state = 'renamed'
            new_module_name = renamed_modules[module_name]
        elif module_name in merged_modules:
            name_state = 'merged'
            new_module_name = merged_modules[module_name]
        else:
            name_state = 'nothing'
            new_module_name = module_name

        # Try to get initial and final module versions
        initial_versions = OodooModuleVersion.search([
            ('technical_name', '=', module_name),
            ('serie_id', '=', self.initial_serie_id.id),
        ])
        if len(initial_versions) > 1:
            exceptions.Warning(_(
                "Many Module Version found for the module %s"
                ", version %s" % (
                    module_name, self.initial_serie_id.name)))

        final_versions = OodooModuleVersion.search([
            ('technical_name', '=', new_module_name),
            ('serie_id', '=', self.final_serie_id.id),
        ])
        if len(final_versions) > 1:
            exceptions.Warning(_(
                "Many Module Version found for the module %s"
                ", version %s" % (
                    new_module_name, self.initial_serie_id.name)))

        return new_module_name, name_state,\
            initial_versions and initial_versions[0],\
            final_versions and final_versions[0],

    def _parse_openupgrade_coverage_file(self):
        """
        Parse the Openupgrade coverage file, and return a dict of key,value
        {'module_name_1': 'state_1', ...}
        """
        if not self.openupgrade_coverage_url:
            return
        self.ensure_one()
        table_data = ""
        data = urlopen(Request(
            self.openupgrade_coverage_url)).read().decode('utf-8')
        for parse_value in self._BEGIN_TABLE_PARSE_VALUES:
            if parse_value in data:
                table_data = data.split(parse_value)[1]
        data_list_tmp = []
        res = {}
        for parse_value in self._LINE_SPLIT_PARSE_VALUES:
            if parse_value in table_data:
                data_list_tmp = table_data.split(parse_value)
        for item in data_list_tmp:
            if '|new|' in item:
                item = item.replace('|new|', '')
            if '|del|' in item:
                item = item.replace('|del|', '')
            module_data = item.replace("\n", "").split("|")
            module_data = [
                x.strip() for x in module_data if x not in ['', ', ']]
            if len(module_data) >= 2:
                module_name = module_data[0]
                coverage_state_text = module_data[1]
                coverage_state = 'todo_migration'

                for k, v in self._MAPPING_ANALYSIS.items():
                    if k in coverage_state_text:
                        coverage_state = v
                res[module_name] = coverage_state

        self.coverage_text = res

    def _parse_openupgrade_module_file(self):
        """
        Parse the Openupgrade merged module file,
        and return a dict of key,value
        {'module_name_1': 'new_module_name_1', ...}
        """
        if not self.openupgrade_module_url:
            return
        res = {}
        self.ensure_one()
        data = urlopen(Request(
            self.openupgrade_module_url)).read().decode('utf-8')

        # Get Renamed modules data
        table_data = data.split("_oca_odoo_renamed_modules = {\n")[1]
        table_data = table_data.split("\n}")[0]
        self.renamed_module_text = eval("{" + table_data + "}")

        # Get Merged modules data
        table_data = data.split("_oca_odoo_merged_modules = [\n")[1]
        table_data = table_data.split("\n]")[0]
        my_list = eval("[" + table_data + "]")
        res = {}
        for item in my_list:
            res[item[0]] = item[1]
        self.merged_module_text = res
