import os
import re
import io
import logging
from seventweets.db import get_db
from importlib import import_module


logger = logging.getLogger(__name__)


MIGRATION_TEMPLATE = '''
"""
{name}
"""
id = {id}


def upgrade(cursor):
    pass


def downgrade(cursor):
    pass
'''


class MigrationManager:
    """
    This class manages migrations and performs upgrade and downgrade actions.

    Migration is defined as python module in `seventweets.migrations` package.
    All migrations have to have `id` module level field that indicate its
    order, `upgrade` and `downgrade` functions that accept `pg8000.Cursor`
    as parameter.

    If direction for migrations is 'upgrade', all will be performed
    If direction for migrations is 'downgrade' only one will be performed. This
    is done for safety and since generally downgrade migrations are not very
    often and are destructive.
    """
    UP = 'up'
    DOWN = 'down'

    def __init__(self, version_table='_migrations'):
        """
        :param version_table: Name of table to hold current migration status.
        """
        self.version_table = version_table
        self.db = get_db()
        self.ensure_infrastructure()
        self.migrations = self.collect_migrations()

        logger.info('Found %d migrations. Last applied id is %s.',
                    len(self.migrations), self.current_version())

    @staticmethod
    def collect_migrations():
        """
        Collects and returns all migrations that could be found.

        Migrations will be found if they inherit `Migrations` class. Also, note
        that module where migrations are defined needs to be executed in order
        for `__subclasses__` method to work.
        """
        migrations = []
        basedir = os.path.dirname(__file__)
        for fmodule in os.listdir(os.path.join(basedir, 'migrations')):
            if fmodule == '__init__.py' or fmodule[-3:] != '.py':
                continue
            mig = import_module(f'seventweets.migrations.{fmodule[:-3]}')
            if not hasattr(mig, 'id'):
                logger.warning('Migration %s without "id" field. Skipping.')
                continue
            else:
                migrations.append(mig)
        return sorted(migrations, key=lambda migration: migration.id)

    def migrate(self, direction):
        """
        Executes migrations.

        In case of 'upgrade' migrations, all unapplied will be applied.
        In case of 'downgrade' migration, only one will be applied.
        :param direction:
            Either `MigrationManager.UP` or `MigrationManager.DOWN`.
        """
        if direction not in [self.UP, self.DOWN]:
            raise ValueError(f'Invalid direction: {direction}')
        if direction == self.UP:
            self._upgrade()
        else:
            self._downgrade()

    def _upgrade(self):
        current_version = self.current_version()

        for migration in self.migrations:
            if migration.id > current_version:
                cursor = self.db.cursor()
                try:
                    logger.info('Applying upgrade migration %s (%s).',
                                migration.id, migration.__name__)
                    migration.upgrade(cursor)
                    self.db.commit()
                except Exception:
                    self.db.rollback()
                    raise
                else:
                    self.set_version(migration.id)
                finally:
                    cursor.close()

    def _downgrade(self):
        current_version = self.current_version()
        current_index = -1
        for i, migrations in enumerate(self.migrations):
            if migrations.id == current_version:
                current_index = i

        cursor = self.db.cursor()
        try:
            migration = self.migrations[current_index]
            logger.info('Applying downgrade migration %s (%s).',
                        migration.id, migration.__name__)
            migration.downgrade(cursor)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        else:
            if current_index == 0:
                self.set_version(0)
            else:
                prev_migration = self.migrations[current_index - 1]
                self.set_version(prev_migration.id)
        finally:
            cursor.close()

    def ensure_infrastructure(self):
        """
        Makes sure that table for tracking migration exists in database.
        """
        cur = self.db.cursor()
        cur.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.version_table}
            (
                version integer
            );
        ''')
        self.db.commit()
        cur.close()

    def current_version(self):
        """
        Returns currently applied migration from database.
        """
        cur = self.db.cursor()
        cur.execute(f'''
            SELECT version FROM {self.version_table} LIMIT 1;
        ''')
        cur_version = cur.fetchone()
        if cur_version is None:
            version = 0
        else:
            version = cur_version[0]

        cur.close()
        return version

    def set_version(self, version):
        """
        Sets version to migration table in database.
        :param version: Version to set.
        """
        cur = self.db.cursor()
        cur.execute(f'''
            SELECT count(*) FROM {self.version_table};
        ''')
        count = cur.fetchone()[0]
        if count == 0:
            cur.execute(f'''
                INSERT INTO {self.version_table} (version) VALUES (%s);
            ''', (version,))
        else:
            cur.execute(f'''
                UPDATE {self.version_table} SET version=%s;
            ''', (version,))
        self.db.commit()
        cur.close()

    def create_migration(self, name):
        """
        Generates new migration skeleton.

        In `seventweets.migrations` module, new file will be created. Name is
        generated from provided name (normalized first) and content of the
        file contains skeleton for valid migration.

        :param name: Name of migration to generate.
        """
        logger.info('Creating new migration: %s', name)
        basedir = os.path.dirname(__file__)

        # determine next migration ID
        current_max = max(self.migrations, key=lambda m: m.id)
        next_id = current_max.id + 1

        # normalize file name to valid python identificator and calculate path
        # to file for new migration
        normalized_name = re.sub('\W|^(?=\d)', '_', name)
        file_name = f'{next_id:0>3}_{normalized_name}.py'
        file_path = os.path.join(basedir, 'migrations', file_name)

        # just in case, check if file already exist since it might exist
        # without being proper migration (without `id` field), in which
        # case we would not catch it on collection
        if os.path.exists(file_name):
            raise ValueError(
                'File %s already exist and it is not migration. Remove it, '
                'since `seventweets.migrations` should contain only migration '
                'files', file_path,
            )

        # write file content based on template and calculated values
        with io.open(file_path, 'w') as mig_file:
            mig_file.write(MIGRATION_TEMPLATE.format(id=next_id, name=name))

        logger.info('Migration %s generated.', file_path)


def test_migrations():
    migrations = {}
    basedir = os.path.dirname(__file__)
    for module in os.listdir(os.path.join(basedir, 'migrations')):
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        mig = import_module(f'seventweets.migrations.{module[:-3]}')
        if not hasattr(mig, 'id'):
            logger.warning('Migration %s without "id" field. Skipping.',
                           mig.__name__)
            continue
        else:
            migrations[mig.id] = mig
    print(migrations)
