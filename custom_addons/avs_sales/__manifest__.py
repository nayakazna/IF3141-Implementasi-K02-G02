# -*- coding: utf-8 -*-
{
    "name": "AVS Sales",
    "version": "1.0",
    "category": "Sales/CRM",
    "summary": "Pengelolaan kebutuhan teknis awal proyek dari proses CRM",
    "description": """
        Menambahkan field kebutuhan teknis awal pada Lead/Opportunity
        untuk mendukung proses analisis kebutuhan proyek.
    """,
    "author": "Kelompok 02 - K02",
    "depends": [
        "crm",
        "avs_project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/avs_simulator_type_data.xml",
        "views/crm_lead_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
