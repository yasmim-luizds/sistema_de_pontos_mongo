import logging
import logging.config
import sys
from pathlib import Path
# autor: Elias 
import cx_Oracle  # type: ignore[import-not-found]
from pymongo import MongoClient


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    # 'incremental': True,  # Default: False
    'formatters': {
        'console_fmt': {
            'format': '%(asctime)s | %(levelname)8s | %(name)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            # 'level': logging.DEBUG,
            'formatter': 'console_fmt',
            # 'filter': '',
            # 'stream': 'ext://sys.stdout',  # default is stderr
        },
    },
    'loggers': {
        '': {  # 'root' logger
            'handlers': ['console'],
            'level': logging.WARNING,
        },
        __name__: {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        }
    },
}

# logging.basicConfig(level=logging.NOTSET)
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

# FIXME: Move secrets to a .env file
MONGO_ADMIN_USER = 'mongoadmin'
MONGO_ADMIN_PASS = 'secret'  # nosec B105

ORACLE_ADMIN_USER = 'system'
ORACLE_ADMIN_PASS = 'oracle'  # nosec B105


def create_mongo_user_lab(
    admin_user: str,
    admin_pass: str,
) -> None:
    authentication_mongo_file = Path(__file__).parent / 'conexion/passphrase/authentication.mongo'
    lab_user, lab_pass = authentication_mongo_file.read_text().split(',')

    lab_db_name = 'labdatabase'
    admin_db_name = 'admin'

    mongo_client: MongoClient = MongoClient(  # nosec B106
        username=admin_user,
        password=admin_pass,
    )
    db = mongo_client[admin_db_name]

    res = db.command('usersInfo', lab_user)
    created = bool(len(res['users']))
    logger.info(f'[mongo] User already exists: {created}.')

    if not created:
        db.command(
            'createUser',
            lab_user,
            pwd=lab_pass,
            roles=[{'role': 'readWrite', 'db': lab_db_name}],
        )
        res = db.command('usersInfo', lab_user)
        created = bool(len(res['users']))
        logger.info(f'[mongo] User now exists: {created}.')
    else:
        logger.info(f'[mongo] Granting the "{lab_user}" permission to the database "{lab_db_name}".')
        db.command(
            'grantRolesToUser',
            lab_user,
            roles=[{'role': 'readWrite', 'db': lab_db_name}],
        )

    mongo_client.close()


def create_oracle_user_lab(
    admin_user: str,
    admin_pass: str,
    force: bool = False,
) -> None:
    authentication_oracle_file = Path(__file__).parent / 'conexion/passphrase/authentication.oracle'
    lab_user, lab_pass = authentication_oracle_file.read_text().split(',')

    host = 'localhost'
    port = 1521
    service_name = 'XEPDB1'
    # sid = 'XE'
    conn_string = cx_Oracle.makedsn(
        host=host,
        port=port,
        service_name=service_name,
    )

    logger.info('[oracle] Connecting to Oracle DB...')
    conn = cx_Oracle.connect(
        user=admin_user,
        password=admin_pass,
        dsn=conn_string,
    )
    cursor = conn.cursor()

    res = cursor.execute(
        'SELECT 1 FROM all_users WHERE username = :username',
        {'username': lab_user.upper()}
    )
    user_exist = res.fetchone() is not None

    logger.info(f'[oracle] User exists: {lab_user.upper()}.')

    if not user_exist or force:
        logger.info(f'[oracle] (Re-)creating user: "{lab_user}".')

        if force:
            cursor.execute(f'DROP USER {lab_user} CASCADE')

        cursor.execute(f'CREATE USER {lab_user} IDENTIFIED BY "{lab_pass}"')

        # Privilégios
        cursor.execute(f'GRANT CREATE SESSION TO {lab_user}')
        cursor.execute(f'GRANT CREATE TABLE TO {lab_user}')
        cursor.execute(f'GRANT CREATE SEQUENCE TO {lab_user}')
        cursor.execute(f'GRANT CREATE VIEW TO {lab_user}')
        cursor.execute(f'GRANT CREATE PROCEDURE TO {lab_user}')

        # Permissão para usar tablespace USERS
        cursor.execute(f'ALTER USER {lab_user} QUOTA UNLIMITED ON USERS')

        # Profile (somente 1 statement por execute?)
        cursor.execute('ALTER PROFILE DEFAULT LIMIT PASSWORD_LIFE_TIME UNLIMITED')

        conn.commit()

    else:
        logger.warning(f'[oracle] User "{lab_user}".')

if __name__ == '__main__':
    force = sys.argv[1] == '--force' if len(sys.argv) > 1 else False

    create_mongo_user_lab(
        admin_user=MONGO_ADMIN_USER,
        admin_pass=MONGO_ADMIN_PASS,
    )
    create_oracle_user_lab(
        admin_user=ORACLE_ADMIN_USER,
        admin_pass=ORACLE_ADMIN_PASS,
        force=force,
    )
