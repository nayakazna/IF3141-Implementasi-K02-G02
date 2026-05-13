# -*- coding: utf-8 -*-
{
    "name": "AVS Material & Procurement",
    "version": "1.0",
    "category": "Inventory",
    "summary": "Pendataan inventaris dan request pengadaan material",
    "description": """
        Mengelola stok komponen fisik dan form pengajuan pengadaan
        ke supplier apabila stok di bawah batas minimum.
    """,
    "author": "Kelompok 02 - K02",
    "depends": [
        "base",
        "project",
        "avs_project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/avs_sequence_data.xml",
        "views/avs_material_views.xml",
        "views/avs_procurement_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}