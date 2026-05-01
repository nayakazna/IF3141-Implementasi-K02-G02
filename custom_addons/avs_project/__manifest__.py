# -*- coding: utf-8 -*-
{
    'name': 'AVS Project Management',
    'version': '1.0',
    'category': 'Project',
    'summary': 'Modul manajemen proyek custom untuk PT AVS',
    'description': """
        Memanajemen proyek dengan fitur perhitungan progress otomatis berdasarkan status task dan sub-task, serta manajemen beban kerja pengguna.
    """,
    'author': 'Kelompok 02 - K02',
    'website': 'https://www.avsimulator.com',
    'depends': [
        'base', 
        'project',
    ],
    'data': [
        'security/avs_security.xml',
        'security/ir.model.access.csv',
        'views/avs_project_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}