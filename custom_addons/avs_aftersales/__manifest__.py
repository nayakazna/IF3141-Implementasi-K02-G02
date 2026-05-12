# -*- coding: utf-8 -*-
{
    "name": "AVS Aftersales",
    "version": "1.0",
    "category": "Project",
    "summary": "Pencatatan dan penerusan laporan aftersales",
    "description": """
        Mengelola laporan aftersales, status penanganan, dan proses
        penerusan laporan ke pihak yang bertanggung jawab.
    """,
    "author": "Kelompok 02 - K02",
    "depends": [
        "base",
        "mail",
        "project",
        "avs_project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/avs_aftersales_report_security.xml",
        "data/avs_aftersales_sequence.xml",
        "views/avs_aftersales_report_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
