{
    'name' : 'Building Management System',
    'version' : '1.0',
    'author' : 'Jakc Labs',
    'category' : 'Generic Modules/Building Management System',
    'depends' : ['base_setup','base','hr', 'product', 'account', 'sale'],
    'init_xml' : [],
    'data' : [                                                
        'jakc_bm_lot_view.xml',
        'jakc_bm_lease_view.xml',
        'jakc_bm_customer_view.xml',
        'jakc_bm_menu.xml',         
        'jakc_bm_config_view.xml',
        'jakc_bm_config_menu.xml',   
        'security/jakc_bm_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}