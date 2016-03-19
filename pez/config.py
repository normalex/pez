import os

DEFAULT_MAX_COUNT = 100

def get_configuration(conf):
    return dict(
        dbhost=conf.get('PEZ_DB_HOST', 'localhost'),
        dbport=conf.get('PEZ_DB_PORT', 5432),
        dbname=conf.get('PEZ_DB_NAME', 'pez'),
        dbusername=conf.get('PEZ_DB_USERNAME', 'pezuser'),
        dbpassword=conf.get('PEZ_DB_PASSWORD', 'secretpassword'),
        max_count=int(
            conf.get('PEZ_MAX_COUNT', str(DEFAULT_MAX_COUNT)),
            10
        ) or DEFAULT_MAX_COUNT
    )

configuration = get_configuration(os.environ)

