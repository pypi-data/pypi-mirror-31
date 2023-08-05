import contextlib as cl
import datetime as dt
import pathlib as pl
import re
import sqlite3
import threading
from typing import Any, Dict, List, Text, Union

from . import util as u


SQL_CREATE_TABLES = [
    '''
    CREATE TABLE metadata (
        key VARCHAR(64) NOT NULL,
        value VARCHAR(4096),
        PRIMARY KEY (key)
    );
    ''',
    '''
    CREATE TABLE nodes (
        id VARCHAR(32) NOT NULL,
        name VARCHAR(4096),
        status VARCHAR(16),
        created DATETIME,
        modified DATETIME,
        PRIMARY KEY (id),
        UNIQUE (id),
        CHECK (status IN ('AVAILABLE', 'TRASH'))
    );
    ''',
    '''
    CREATE TABLE files (
        id VARCHAR(32) NOT NULL,
        md5 VARCHAR(32),
        size BIGINT,
        PRIMARY KEY (id),
        UNIQUE (id),
        FOREIGN KEY (id) REFERENCES nodes (id)
    );
    ''',
    '''
    CREATE TABLE parentage (
        parent VARCHAR(32) NOT NULL,
        child VARCHAR(32) NOT NULL,
        PRIMARY KEY (parent, child),
        FOREIGN KEY (child) REFERENCES nodes (id)
    );
    ''',
    'CREATE INDEX ix_parentage_child ON parentage(child);',
    'CREATE INDEX ix_nodes_names ON nodes(name);',
    'PRAGMA user_version = 1;',
]

CURRENT_SCHEMA_VERSION = 1


class DatabaseError(u.GoogleDriveError):

    def __init__(self, message: Text) -> None:
        super(DatabaseError, self).__init__()

        self._message = message

    def __str__(self) -> Text:
        return self._message


class Database(object):

    def __init__(self, settings: u.Settings) -> None:
        self._settings = settings
        self._tls = threading.local()

    def __enter__(self) -> 'Database':
        try:
            self._try_create()
        except sqlite3.OperationalError as e:
            pass

        db = self._get_thread_local_database()
        with ReadOnly(db) as query:
            query.execute('PRAGMA user_version;')
            rv = query.fetchone()
        version = rv[0]

        if CURRENT_SCHEMA_VERSION > version:
            self._migrate(version)

        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        db = self._get_thread_local_database()
        db.close()

    @property
    def root_id(self) -> Text:
        return self.get_metadata('root_id')

    @property
    def root_node(self) -> 'Node':
        return self.get_node_by_id(self.root_id)

    def get_metadata(self, key: Text) -> Text:
        db = self._get_thread_local_database()
        with ReadOnly(db) as query:
            query.execute('SELECT value FROM metadata WHERE key = ?;', (key,))
            rv = query.fetchone()
        if not rv:
            raise KeyError
        return rv['value']

    def set_metadata(self, key: Text, value: Text) -> None:
        db = self._get_thread_local_database()
        with ReadWrite(db) as query:
            query.execute('''
                INSERT OR REPLACE INTO metadata
                VALUES (?, ?)
            ;''', (key, value))

    def get_node_by_id(self, node_id: Text) -> Union['Node', None]:
        db = self._get_thread_local_database()
        with ReadOnly(db) as query:
            query.execute('''
                SELECT id, name, status, created, modified
                FROM nodes
                WHERE id=?
            ;''', (node_id,))
            rv = query.fetchone()
            if not rv:
                return None
            node = dict(rv)

            query.execute('''
                SELECT id, md5, size
                FROM files
                WHERE id=?
            ;''', (node_id,))
            rv = query.fetchone()
            is_folder = rv is None
            node['is_folder'] = is_folder
            node['md5'] = None if is_folder else rv['md5']
            node['size'] = None if is_folder else rv['size']

            query.execute('''
                SELECT parent, child
                FROM parentage
                WHERE child=?
            ;''', (node_id,))
            rv = query.fetchall()
            node['parents'] = None if not rv else [_['parent'] for _ in rv]

            node = Node.from_database(node)
            return node

    def get_node_by_path(self, path: Text) -> Union['Node', None]:
        path = pl.Path(path)
        parts = list(path.parts)
        if parts[0] != '/':
            raise Exception('invalid path')

        node_id = self.root_id
        parts.pop(0)
        db = self._get_thread_local_database()
        with ReadOnly(db) as query:
            for part in parts:
                query.execute('''
                    SELECT nodes.id AS id
                    FROM parentage
                        INNER JOIN nodes ON parentage.child=nodes.id
                    WHERE parentage.parent=? AND nodes.name=?
                ;''', (node_id, part))
                rv = query.fetchone()
                if not rv:
                    return None
                node_id = rv['id']

            node = self.get_node_by_id(node_id)
        return node

    def get_path_by_id(self, node_id: Text) -> Union[Text, None]:
        parts = []
        db = self._get_thread_local_database()
        with ReadOnly(db) as query:
            while True:
                query.execute('''
                    SELECT name
                    FROM nodes
                    WHERE id=?
                ;''', (node_id,))
                rv = query.fetchone()
                if not rv:
                    return None

                name = rv['name']
                if not name:
                    parts.insert(0, '/')
                    break
                parts.insert(0, name)

                query.execute('''
                    SELECT parent
                    FROM parentage
                    WHERE child=?
                ;''', (node_id,))
                rv = query.fetchone()
                if not rv:
                    # orphan node
                    break
                node_id = rv['parent']

        path = pl.Path(*parts)
        return str(path)

    def get_child_by_name_from_parent_id(self,
            name: Text,
            parent_id: Text
        ) -> Union['Node', None]:
        db = self._get_thread_local_database()
        with ReadOnly(db) as query:
            query.execute('''
                SELECT nodes.id AS id
                FROM nodes
                    INNER JOIN parentage ON parentage.child=nodes.id
                WHERE parentage.parent=? AND nodes.name=?
            ;''', (parent_id, name))
            rv = query.fetchone()

        if not rv:
            return None

        node = self.get_node_by_id(rv['id'])
        return node

    def get_children_by_id(self, node_id: Text) -> List['Node']:
        db = self._get_thread_local_database()
        with ReadOnly(db) as query:
            query.execute('''
                SELECT child
                FROM parentage
                WHERE parent=?
            ;''', (node_id,))
            rv = query.fetchall()

        children = [self.get_node_by_id(_['child']) for _ in rv]
        return children

    def apply_changes(self,
            changes: Dict[Text, Any],
            check_point: Text,
        ) -> None:
        db = self._get_thread_local_database()
        with ReadWrite(db) as query:
            for change in changes:
                is_removed = change['removed']
                if is_removed:
                    inner_delete_node_by_id(query, change['fileId'])
                else:
                    node = Node.from_api(change['file'])
                    inner_insert_node(query, node)

            self.set_metadata('check_point', check_point)

    def insert_node(self, node: 'Node') -> None:
        db = self._get_thread_local_database()
        with ReadWrite(db) as query:
            inner_insert_node(query, node)

        if not node.name:
            self.set_metadata('root_id', node.id_)

    def find_nodes_by_regex(self, pattern: Text) -> List['Node']:
        db = self._get_thread_local_database()
        with ReadOnly(db) as query:
            query.execute('SELECT id FROM nodes WHERE name REGEXP ?;', (pattern,))
            rv = query.fetchall()
        rv = [self.get_node_by_id(_['id']) for _ in rv]
        return rv

    def find_duplicate_nodes(self) -> List['Node']:
        db = self._get_thread_local_database()
        with ReadOnly(db) as query:
            query.execute('''
                SELECT nodes.name AS name, parentage.parent as parent_id
                FROM nodes
                    INNER JOIN parentage ON parentage.child=nodes.id
                GROUP BY parentage.parent, nodes.name
                HAVING COUNT(*) > 1
            ;''')
            name_parent_pair = query.fetchall()

            node_id_list = []
            for pair in name_parent_pair:
                query.execute('''
                    SELECT nodes.id AS id
                    FROM nodes
                        INNER JOIN parentage ON parentage.child=nodes.id
                    WHERE parentage.parent=? AND nodes.name=?
                ;''', (pair['parent_id'], pair['name']))
                rv = query.fetchall()
                rv = (_['id'] for _ in rv)
                node_id_list.extend(rv)

            rv = [self.get_node_by_id(_) for _ in node_id_list]
        return rv

    def find_orphan_nodes(self) -> List['Node']:
        db = self._get_thread_local_database()
        with ReadOnly(db) as query:
            query.execute('''
                SELECT nodes.id AS id
                FROM parentage
                    LEFT OUTER JOIN nodes ON parentage.child=nodes.id
                WHERE parentage.parent IS NULL
            ;''')
            rv = query.fetchall()
            rv = [self.get_node_by_id(_['id']) for _ in rv]
        return rv

    def _get_thread_local_database(self) -> sqlite3.Connection:
        db = getattr(self._tls, 'db', None)
        if db is None:
            db = self._open()
            setattr(self._tls, 'db', db)
        return db

    def _open(self) -> sqlite3.Connection:
        path = self._settings['nodes_database_file']
        db = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        db.row_factory = sqlite3.Row
        db.create_function('REGEXP', 2, sqlite3_regexp)
        return db

    def _try_create(self) -> None:
        db = self._get_thread_local_database()
        with ReadWrite(db) as query:
            for sql in SQL_CREATE_TABLES:
                query.execute(sql)

    def _migrate(self, version) -> None:
        raise NotImplementedError()


class Node(object):

    @staticmethod
    def from_api(data: Dict[Text, Any]) -> 'Node':
        node = Node(data)
        node._initialize_from_api()
        return node

    @staticmethod
    def from_database(data: Dict[Text, Any]) -> 'Node':
        node = Node(data)
        node._initialize_from_database()
        return node

    def __init__(self, data: Dict[Text, Any]) -> None:
        self._data = data

    @property
    def is_root(self) -> bool:
        return self._name is None

    @property
    def is_file(self) -> bool:
        return not self._is_folder

    @property
    def is_folder(self) -> bool:
        return self._is_folder

    @property
    def id_(self) -> Text:
        return self._id

    @property
    def name(self) -> Text:
        return self._name

    @property
    def status(self) -> Text:
        return self._status

    @property
    def is_available(self) -> bool:
        return self._status == 'AVAILABLE'

    @property
    def is_trashed(self) -> bool:
        return self._status == 'TRASH'

    @is_trashed.setter
    def is_trashed(self, trashed: bool) -> None:
        if trashed:
            self._status = 'TRASH'
        else:
            self._status = 'AVAILABLE'

    @property
    def created(self) -> dt.datetime:
        return self._created

    @property
    def modified(self) -> dt.datetime:
        return self._modified

    @property
    def parents(self) -> List[Text]:
        return self._parents

    @property
    def parent_id(self) -> Text:
        if len(self._parents) != 1:
            msg = 'expected only one parent, got: {0}'.format(self._parents)
            raise DatabaseError(msg)
        return self._parents[0]

    @property
    def md5(self) -> Text:
        return self._md5

    @property
    def size(self) -> int:
        return self._size

    def _initialize_from_api(self) -> None:
        data = self._data
        self._id = data['id']
        self._name = data['name']
        self._status = 'TRASH' if data['trashed'] else 'AVAILABLE'
        self._created = u.from_isoformat(data['createdTime'])
        self._modified = u.from_isoformat(data['modifiedTime'])
        self._parents = data.get('parents', None)

        self._is_folder = data['mimeType'] == u.FOLDER_MIME_TYPE
        self._md5 = data.get('md5Checksum', None)
        self._size = data.get('size', None)

    def _initialize_from_database(self) -> None:
        data = self._data
        self._id = data['id']
        self._name = data['name']
        self._status = data['status']
        self._created = data['created']
        self._modified = data['modified']
        self._parents = data.get('parents', None)

        self._is_folder = data['is_folder']
        self._md5 = data['md5']
        self._size = data['size']


class ReadOnly(object):

    def __init__(self, db: sqlite3.Connection) -> None:
        self._db = db

    def __enter__(self) -> sqlite3.Cursor:
        self._cursor = self._db.cursor()
        return self._cursor

    def __exit__(self, exc_type, exc_value, exc_tb) -> bool:
        self._cursor.close()


class ReadWrite(object):

    def __init__(self, db: sqlite3.Connection) -> None:
        self._db = db

    def __enter__(self) -> sqlite3.Cursor:
        self._cursor = self._db.cursor()
        return self._cursor

    def __exit__(self, exc_type, exc_value, exc_tb) -> bool:
        if exc_type is None:
            self._db.commit()
        else:
            self._db.rollback()
        self._cursor.close()


def inner_insert_node(query: sqlite3.Cursor, node: Node) -> None:
    # add this node
    query.execute('''
        INSERT OR REPLACE INTO nodes
        (id, name, status, created, modified)
        VALUES
        (?, ?, ?, ?, ?)
    ;''', (node.id_, node.name, node.status, node.created, node.modified))

    # add file information
    if not node.is_folder:
        query.execute('''
            INSERT OR REPLACE INTO files
            (id, md5, size)
            VALUES
            (?, ?, ?)
        ;''', (node.id_, node.md5, node.size))

    # add parentage
    if node.parents:
        query.execute('''
            DELETE FROM parentage
            WHERE child=?
        ;''', (node.id_,))

        for parent in node.parents:
            query.execute('''
                INSERT OR REPLACE INTO parentage
                (parent, child)
                VALUES
                (?, ?)
            ;''', (parent, node.id_))


def inner_delete_node_by_id(query: sqlite3.Cursor, node_id: Text) -> None:
    # disconnect parents
    query.execute('''
        DELETE FROM parentage
        WHERE child=? OR parent=?
    ;''', (node_id, node_id))

    # remove from files
    query.execute('''
        DELETE FROM files
        WHERE id=?
    ;''', (node_id,))

    # remove from nodes
    query.execute('''
        DELETE FROM nodes
        WHERE id=?
    ;''', (node_id,))


def sqlite3_regexp(pattern: Text, cell: Union[Text, None]) -> bool:
    if cell is None:
        # root node
        return False
    return re.search(pattern, cell, re.I) is not None


def initialize() -> None:
    sqlite3.register_adapter(dt.datetime, lambda _: _.isoformat())
    sqlite3.register_converter('DATETIME', to_dt)


def to_dt(raw_datetime):
    s = raw_datetime.decode('utf-8')
    return u.from_isoformat(s)


initialize()
