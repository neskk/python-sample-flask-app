#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import sys

from peewee import *
from playhouse.pool import PooledMySQLDatabase
from playhouse.migrate import migrate, MySQLMigrator

from datetime import datetime, timedelta
from enum import IntEnum

log = logging.getLogger(__name__)

# https://docs.peewee-orm.com/en/latest/peewee/database.html#dynamically-defining-a-database
# https://docs.peewee-orm.com/en/latest/peewee/playhouse.html#database-url
db = DatabaseProxy()
db_schema_version = 1
db_step = 250

#db = SqliteDatabase('sqlite-debug.db')


def init_database(db_name, db_host, db_port, db_user, db_pass):
    """ Create a pooled connection to MySQL database """
    log.info('Connecting to MySQL database on %s:%i...', db_host, db_port)

    database = PooledMySQLDatabase(
        db_name,
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
        stale_timeout=60,
        max_connections=None,
        charset='utf8mb4')

    # Initialize DatabaseProxy
    db.initialize(database)

    try:
        verify_database_schema()
        verify_table_encoding(db_name)
    except Exception as e:
        log.exception('Failed to verify database schema: %s', e)
        sys.exit(1)
    return db

# Enum Classes
class Protocol(IntEnum):
    HTTP = 0
    SOCKS4 = 1
    SOCKS5 = 2

class Status(IntEnum):
    OK = 0
    UNKNOWN = 1
    ERROR = 2
    TIMEOUT = 3
    BANNED = 4

# https://docs.peewee-orm.com/en/latest/peewee/models.html#field-types-table
# Custom field types
class Utf8mb4CharField(CharField):
    def __init__(self, max_length=191, *args, **kwargs):
        self.max_length = max_length
        super(CharField, self).__init__(*args, **kwargs)


class UBigIntegerField(BigIntegerField):
    field_type = 'bigint unsigned'


class UIntegerField(IntegerField):
    field_type = 'int unsigned'


class USmallIntegerField(SmallIntegerField):
    field_type = 'smallint unsigned'


# https://docs.peewee-orm.com/en/latest/peewee/models.html#model-options-and-table-metadata
# https://docs.peewee-orm.com/en/latest/peewee/models.html#meta-primary-key
class BaseModel(Model):
    class Meta:
        database = db

    @classmethod
    def database(cls):
        return cls._meta.database

    @classmethod
    def get_all(cls):
        return [m for m in cls.select().dicts()]


class SampleModel(BaseModel):
    integer = UIntegerField(unique=True)
    small_integer = USmallIntegerField()
    ip = IPField()
    enum = USmallIntegerField(index=True)
    emoji_text = Utf8mb4CharField(null=True, max_length=32)
    creation_date = DateTimeField(index=True, default=datetime.utcnow)
    modified_date = DateTimeField(index=True, null=True)

    class Meta:
        primary_key = CompositeKey('integer', 'small_integer')

    @staticmethod
    def db_format(obj):
        """ Format object into valid database form """
        return {
            'integer': obj['integer'],
            'small_integer': obj['small_integer'],
            'ip': obj['ip'],
            'enum': obj['protocol'],
            'emoji_text': obj['emoji_text'],
            'creation_date': obj.get('creation_date', datetime.utcnow()),
            'modified_date': obj.get('modified_date', None)
        }

    @staticmethod
    def get_by_ip(ip):
        try:
            query = (SampleModel
                     .select_query()
                     .where(SampleModel.ip == ip)
                     .dicts())
            if len(query) > 0:
                return query[0]

        except OperationalError as e:
            log.exception('Failed to get model by IP from database: %s', e)

        return None


class Version(BaseModel):
    """ Database versioning model """
    key = Utf8mb4CharField()
    val = SmallIntegerField()

    class Meta:
        primary_key = False


MODELS = [SampleModel, Version]


def create_tables():
    """ Create tables in the database (skips existing) """
    with db:
        for table in MODELS:
            if not table.table_exists():
                log.info('Creating database table: %s', table.__name__)
                db.create_tables([table], safe=True)
            else:
                log.debug('Skipping database table %s, it already exists.',
                          table.__name__)


def drop_tables():
    """ Drop all the tables in the database """
    with db:
        db.execute_sql('SET FOREIGN_KEY_CHECKS=0;')
        for table in MODELS:
            if table.table_exists():
                log.info('Dropping database table: %s', table.__name__)
                db.drop_tables([table], safe=True)

        db.execute_sql('SET FOREIGN_KEY_CHECKS=1;')

# https://docs.peewee-orm.com/en/latest/peewee/playhouse.html#schema-migrations
def migrate_database_schema(old_ver):
    """ Migrate database schema """
    log.info('Detected database version %i, updating to %i...',
             old_ver, db_schema_version)

    with db:
        # Update database schema version
        query = (Version
                 .update(val=db_schema_version)
                 .where(Version.key == 'schema_version'))
        query.execute()

    # Perform migrations here
    migrator = MySQLMigrator(db)

    if old_ver < 2:
        # Remove hash field unique index
        migrate(migrator.drop_index('sample_model', 'sample_model_hash'))
        # Reset hash field in all rows
        SampleModel.update(hash=1).execute()
        # Modify column type
        db.execute_sql(
            'ALTER TABLE `sample_model` '
            'CHANGE COLUMN `hash` `hash` INT UNSIGNED NOT NULL;'
        )
        # Re-hash all rows
        SampleModel.rehash_all()
        # Recreate hash field unique index
        migrate(migrator.add_index('sample_model', ('hash',), True))

    if old_ver < 3:
        # Add another column/field
        migrate(
            migrator.add_column('sample_model', 'another_integer',
                                UIntegerField(index=True, null=True))
        )

    # Always log that we're done.
    log.info('Schema upgrade complete.')
    return True


def verify_database_schema():
    """ Verify if database is properly initialized """
    if not Version.table_exists():
        log.info('Database schema is not created, initializing...')
        create_tables()
        Version.insert(key='schema_version', val=db_schema_version).execute()
    else:
        db_ver = Version.get(Version.key == 'schema_version').val

        if db_ver < db_schema_version:
            if not migrate_database_schema(db_ver):
                log.error('Error migrating database schema.')
                sys.exit(1)

        elif db_ver > db_schema_version:
            log.error('Your database version (%i) seems to be newer than '
                      'the code supports (%i).', db_ver, db_schema_version)
            log.error('Upgrade your code base or drop the database.')
            sys.exit(1)


def verify_table_encoding(db_name):
    """ Verify if table collation is valid """
    with db:
        cmd_sql = '''
            SELECT table_name FROM information_schema.tables WHERE
            table_collation != "utf8mb4_unicode_ci"
            AND table_schema = "%s";''' % db_name
        change_tables = db.execute_sql(cmd_sql)

        cmd_sql = 'SHOW tables;'
        tables = db.execute_sql(cmd_sql)

        if change_tables.rowcount > 0:
            log.info('Changing collation and charset on %s tables.',
                     change_tables.rowcount)

            if change_tables.rowcount == tables.rowcount:
                log.info('Changing whole database, this might a take while.')

            db.execute_sql('SET FOREIGN_KEY_CHECKS=0;')
            for table in change_tables:
                log.debug('Changing collation and charset on table %s.',
                          table[0])
                cmd_sql = '''
                    ALTER TABLE %s CONVERT TO CHARACTER SET utf8mb4
                    COLLATE utf8mb4_unicode_ci;''' % str(table[0])
                db.execute_sql(cmd_sql)
            db.execute_sql('SET FOREIGN_KEY_CHECKS=1;')
