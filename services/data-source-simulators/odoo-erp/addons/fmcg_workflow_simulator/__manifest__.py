{
    "name": "FMCG Workflow Simulator",
    "summary": "Generate traceable raw-material RFQs on a schedule",
    "version": "19.0.1.0.0",
    "category": "Tools",
    "license": "LGPL-3",
    "depends": ["sale_management", "purchase_stock", "account"],
    "data": [
        "security/ir.model.access.csv",
        "data/res_users.xml",
        "data/ir_cron.xml",
        "views/fmcg_simulator_views.xml",
    ],
    "application": True,
    "installable": True,
}
