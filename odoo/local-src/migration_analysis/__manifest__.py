# Copyright (C) 2018-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Migration Analysis',
    'summary': 'Analyse migration',
    'version': '11.0.1.0.0',
    'category': 'Tools',
    'license': 'AGPL-3',
    'author':
        'Odoo Community Association (OCA), GRAP',
    'depends': [
        'github_connector_odoo',
    ],
    'data': [
        'views/migration_analysis.xml',
    ],
    'demo': [
        'demo/migration_analysis.xml',
        'demo/migration_analysis_line.xml',
    ],
    'installable': True,
}
