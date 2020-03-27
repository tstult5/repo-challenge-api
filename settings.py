
DEBUG= True
ENVIRONMENT = 'DEV'


PROTOCOL = 'http'
DOMAIN = '127.0.0.1'
PORT = 5000

BASE_URL = '{}://{}{}'.format(
    PROTOCOL,
    DOMAIN,
    ':{}'.format(PORT) if PORT else ''
)

DATABASES = {
    'dev': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'divvy_dose',
        'USER': 'divvy_dose',
        'PASSWORD': 'divvy_pwd',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

API_CLIENTS = {
     'github':{
         'TIMEOUT_MILLISECONDS':8000,
         'BASE_URL':'https://api.github.com',
         'VERSION':'application/vnd.github.mercy-preview+json'
              },
      'bitbucket':{
         'TIMEOUT_MILLISECONDS':8000,
         'BASE_URL':'https://api.bitbucket.org',
         'VERSION':'2.0'
             }
    }