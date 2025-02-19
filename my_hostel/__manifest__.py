{
    'name': 'Hostel Management',
    'summary': 'Manage Hostel easily',
    'description': "Efficiently manage the entire residential facility in the school.",
    'author': 'Daniel',
    'website': 'http://www.example.com',
    'category': 'Uncategorized',
    'version': '17.0.1.0.0',
    'depends': ['base', 'mail'],
    'data': [
        'security/hostel_security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/room_data.xml',
        'data/room_stages.xml',
        'views/hostel.xml',
        'views/hostel_room.xml',
        'views/hostel_amenities.xml',
        'views/hostel_student.xml',
        'views/hostel_categ.xml',
        'wizards/assign_room_student.xml',
        'views/hostel_room_availability.xml',
        'views/res_config_settings.xml',
        'views/hostel_room_category.xml',
        'views/hostel_room_stage.xml',
        'reports/hostel_room_detail_report.xml',
        'reports/hostel_room_detail_report_template.xml',
        'views/templates.xml',
    ],
    #'pre_init_hook':'pre_init_hook_hostel',
    'post_init_hook': 'add_room_hook',
    #'uninstall_hook': 'uninstall_hook_user',
    #'assets': {
    #    'web.assets_backend': [
    #        'web/static/src/xml/**/*',
    #    ],
    #},
    #'demo': ['demo.xml'],
}
