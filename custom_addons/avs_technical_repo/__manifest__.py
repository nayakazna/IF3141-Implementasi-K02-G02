# -*- coding: utf-8 -*-
{
    "name": "AVS Technical Repository",
    "version": "1.0",
    "category": "Project",
    "summary": "Single source of truth untuk dokumen teknis proyek",
    "description": """
        Mengelola dokumen teknis proyek (DRO, CAD, UAT) dengan
        versioning otomatis, kontrol akses berbasis peran, dan integrasi
        langsung ke aplikasi Project.
    """,
    "author": "Kelompok 02 - K02",
    "depends": [
        "project",
        "avs_project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/avs_technical_repo_security.xml",
        "views/avs_technical_document_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
