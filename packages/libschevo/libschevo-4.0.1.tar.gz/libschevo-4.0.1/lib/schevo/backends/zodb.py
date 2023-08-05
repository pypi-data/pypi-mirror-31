"""ZODB3 backend."""

# Copyright (c) 2001-2009 ElevenCraft Inc.
# See LICENSE for details.

import gevent
from gevent import monkey
monkey.patch_all()

from schevo.database import format_dbclass
from BTrees.OOBTree import OOBTree
from persistent.mapping import PersistentMapping
from persistent.list import PersistentList
from ZODB import DB

from ZEO import ClientStorage
#from ZODB.FileStorage import FileStorage

import transaction
import logging
log = logging.getLogger(__name__)

from gevent import Greenlet

__all__ = ['ZodbBackend', 'ThreadedConnectionPool']


class ZodbBackend(object):

    description = 'Backend that directly uses ZODB 3.7.4'
    backend_args_help = """
    (no backend options)
    """

    __test__ = False

    BTree = OOBTree
    PDict = PersistentMapping
    PList = PersistentList

    #TestMethods_CreatesDatabase = TestMethods_CreatesDatabase
    #TestMethods_CreatesSchema = TestMethods_CreatesSchema
    #TestMethods_EvolvesSchemata = TestMethods_EvolvesSchemata

    def __init__(self, addr):
        self._addr = addr
        self.host, self.port = self._addr.split(':')

        self._is_open = False
        self.open()

    @classmethod
    def args_from_string(cls, s):
        """Return a dictionary of keyword arguments based on a string given
        to a command-line tool."""
        kw = {}
        if s is not None:
            for arg in (p.strip() for p in s.split(',')):
                name, value = (p2.strip() for p2 in arg.split('='))
                raise KeyError(
                    '%s is not a valid name for backend args' % name)
        return kw

    @classmethod
    def usable_by_backend(cls, addr):
        """Return (True, additional_backend_args) if the named file is
        usable by this backend, or False if not."""

        host, port = addr.split(':')
        storage = ClientStorage.ClientStorage((host, int(port)))
        # retrieve the filename of the DB
        filename = storage._info['name']

        f = open(filename, 'rb')
        
        # Get first 128 bytes of file.
        header = f.read(128)
        f.close()
        # Look for ZODB signatures.
        if header[:4] == 'FS21' and 'persistent.mapping' in header:
            return (True, {})
        return False

    def open(self):
        if not self._is_open:
            self.storage = ClientStorage.ClientStorage((self.host, int(self.port)))
            self.zodb = DB(self.storage)
            self.conn = self.zodb.open()
            self._is_open = True

    def get_root(self):
        """Return the connection 'root' object."""
        return self.conn.root()

    @property
    def has_db(self):
        """Return True if the backend has a schevo db."""
        return self.get_root().has_key('SCHEVO')

    def commit(self):
        """Commit the current transaction."""
        transaction.commit()

    def rollback(self):
        """Abort the current transaction."""
        transaction.abort()

    def pack(self):
        """Pack the underlying storage."""
        self.zodb.pack()

    def close(self):
        """Close the underlying storage (and the connection if needed)."""
        self.rollback()
        self.conn.close()
        self.zodb.close()
        self.storage.close()
        self._is_open = False


class ThreadedConnectionPool(object):
    #connection_pool = {'default_db': '127.0.0.1:4343'}

    def __init__(self, d=None, sync=True, debug=True, processes=1):
        if debug:
            if d is not None:
                assert isinstance(d, dict) == True
        
        self.sync = sync    
        self._pool = {}
        for key,value in d.iteritems():
            log.debug("Initializing db: %s" % key)
            result = Greenlet.spawn(self.run, value)
            retval = result.get(block=True)
            result2 = Greenlet.spawn(retval._sync)
            self._pool[key] = retval
            #result2.join()

    def run(self, url):
        DatabaseClass = format_dbclass[2]
        conn = ZodbBackend(url)
        db = DatabaseClass(conn)
        db.db_name = url
        return db

    def __getitem__(self, key):
        try:
            v = self._pool[key]
        except KeyError:
            return None
        return v
