# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from urllib.request import Request, urlopen

from odoo import api, fields, models


class OdooMigration(models.Model):
    _name = 'odoo.migration'
    _order = 'initial_serie_id'

    _BEGIN_TABLE = "+===================================+===================================+\n"
    _LINE_SPLIT = "+-----------------------------------+-----------------------------------+"

    _mapping_analysis = {
        'Done': 'ok',
        'No change': 'ok',
        'Nothing to do': 'ok',
        'work in progress': 'wip',
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
        OdooModuleCoreVersion = self.env['odoo.module.core.version']
        for migration in self:
            data = urlopen(
                Request(migration.odoo_coverage_url)).read().decode('utf-8')
            table_data = data.split(self._BEGIN_TABLE)[1]
            data_list = table_data.split(self._LINE_SPLIT)
            for item in data_list:
                print("====>" + item)
                # TODO, remove "|del| |add| in new feature
                module_data = item.replace("\n", "").split("|")
                
                module_data = [
                    x.strip() for x in module_data if x not in ['', ', ']]
                if len(module_data) >= 2:
                    new_module = False
                    obsolete_version = False
                    module_name = module_data[0]
                    module_state = 'to_migrate'
                    module_state_text = module_data[1]
                    odoo_module = OdooModule.create_if_not_exist(module_name)
                    for k, v in self._mapping_analysis.items():
                        if k in module_state_text:
                            module_state = v
                    print("%s - %s - %s" % (module_name, module_state_text, module_state))
                    if not new_module:
                        previous_version =\
                            OdooModuleCoreVersion.create_if_not_exist(
                                odoo_module, migration.initial_serie_id)
                        previous_version.next_version_state = module_state
