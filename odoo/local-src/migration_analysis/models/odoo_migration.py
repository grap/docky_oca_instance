# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from urllib.request import Request, urlopen

from odoo import api, fields, models


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
        'Done': 'ok',
        'No change': 'ok',
        'Nothing to do': 'ok',
        'work in progress': 'wip',
        'Moved to OCA': 'ok',
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

    def button_analyse_coverage(self):
        OdooModule = self.env['odoo.module']
        for migration in self:
            data_list = self._parse_openupgrade_file()
            for item in data_list:
                new_module = False
                obsolete_version = False
                if '|new|' in item:
                    new_version = True
                    item = item.replace('|new|', '')
                if '|del|' in item:
                    obsolete_version = True
                    item = item.replace('|del|', '')
                module_data = item.replace("\n", "").split("|")
                module_data = [
                    x.strip() for x in module_data if x not in ['', ', ']]
                if len(module_data) >= 2:
                    module_name = module_data[0]
                    module_state = 'to_migrate'
                    module_state_text = module_data[1]
                    odoo_module = OdooModule.create_if_not_exist(module_name)
                    for k, v in self._mapping_analysis.items():
                        if k in module_state_text:
                            module_state = v
###                    if not new_module:
###                        previous_version =\
###                            OdooModuleCoreVersion.create_if_not_exist(
###                                odoo_module, migration.initial_serie_id)
###                        previous_version.next_version_state = module_state
###                    if not obsolete_version:
###                        new_version =\
###                            OdooModuleCoreVersion.create_if_not_exist(
###                                odoo_module, migration.final_serie_id)
###                    else:
###                        # TODO FIXME, doesn't work
###                        previous_version =\
###                            OdooModuleCoreVersion.create_if_not_exist(
###                                odoo_module, migration.initial_serie_id)
###                        previous_version.write({'next_version_state': 'obsolete'})

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
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(data_list)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        return data_list
