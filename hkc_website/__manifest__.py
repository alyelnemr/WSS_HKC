 # -*- coding: utf-8 -*-

{
    'name': "HKC Website Theme",

    'summary': """
        website customization""",

    'description': """""",

    'category': 'Localization',
    'version': '1.10',
    'depends': ['web'],
    'license': 'LGPL-3',
    'auto_install': True,
    'installable': True,
    'assets': {
        'web.assets_frontend': [
            'https://fonts.googleapis.com',
            'https://fonts.gstatic.com',
            'https://fonts.googleapis.com/css2?family=Cairo:wght@200..1000&display=swap"',
            'https://fonts.googleapis.com/css?family=Sofia"',
            # 'hkc_website/static/src/scss/cairofont.scss',
            'hkc_website/static/src/css/web_style.css',

        ],

    },
}
