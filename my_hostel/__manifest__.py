{
    'name': 'Hostel Management',
    'summary': 'Manage Hostel easily',
    'description': "Efficiently manage the entire residential facility in the school.",
    'author': 'Daniel',
    'website': 'http://www.example.com',
    'category': 'Uncategorized',
    'version': '17.0.1.0.0',
    'depends': ['base'],
    'data': [
        'security/hostel_security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/hostel.xml',
        'views/hostel_room.xml',
        'views/hostel_amenities.xml',
        'views/hostel_student.xml',
        'views/hostel_categ.xml',
    ],
    #'assets': {
    #    'web.assets_backend': [
    #        'web/static/src/xml/**/*',
    #    ],
    #},
    #'demo': ['demo.xml'],
}
