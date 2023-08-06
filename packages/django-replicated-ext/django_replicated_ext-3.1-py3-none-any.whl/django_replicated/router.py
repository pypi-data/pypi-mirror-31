# coding: utf-8
from __future__ import unicode_literals

from itertools import chain
import logging
import random
from threading import local
from django.utils.six import string_types
from .utils import import_string, shuffled
from . import settings as default_settings

log = logging.getLogger(__name__)


class ReplicationRouterBase(object):
    """
    A base class to build subrouters on.
    """

    # Timeout for dead databases alive check
    REPLICATED_DATABASE_DOWNTIME = 60

    # List of slave database aliases. Default database is always master.
    REPLICATED_DATABASE_SLAVES = []

    REPLICATED_CHECK_IS_ALIVE = True
    REPLICATED_READ_ONLY_DOWNTIME = default_settings.REPLICATED_READ_ONLY_DOWNTIME
    REPLICATED_READ_ONLY_TRIES = default_settings.REPLICATED_READ_ONLY_TRIES

    # Enable or disable state checking on writes.
    # If disabled, db_for_write will cause side effects (use of master database
    # for further reads).
    REPLICATED_CHECK_STATE_ON_WRITE = True

    # ### Overridable (in many ways) extensible settings management ###

    _settings_tag = "REPLICATED_"

    _context = None

    def _get_setting(self, key):
        tag = self._settings_tag
        if not key.startswith(tag):
            attr = "{}{}".format(tag, key.upper())
        else:
            attr = key
        return getattr(self, attr)

    @classmethod
    def _list_settings(cls):
        tag = cls._settings_tag
        # For DRY extensibility.
        return list(attr for attr in dir(cls) if attr.startswith(tag))

    def _update_from_settings(self, settings):
        """
        Use some settings object to update settings on self.

        WARNING: should be called before going into __init__ of this base class.
        """
        for key in self._list_settings():
            try:
                value = getattr(settings, key)
            except AttributeError:
                pass
            else:
                setattr(self, key, value)

    def _update_from_dict(self, settings):
        """
        Use some convenient-ish dict to update settings on self.

        WARNING: should be called before going into __init__ of this base class.
        """
        for key in self._list_settings():
            dict_key = key[len(self._settings_tag):].lower()
            try:
                value = settings[dict_key]
            except KeyError:
                pass
            else:
                setattr(self, key, value)

    # ### Overridable convenience properties ###

    @property
    def DATABASES(self):
        from django.conf import settings
        return settings.DATABASES

    @property
    def DEFAULT_DB(self):
        from django.db import DEFAULT_DB_ALIAS
        return DEFAULT_DB_ALIAS

    class Context(local):
        """ Thread-local holder of the execution context """

        def __init__(self):
            self.state_stack = []
            self.chosen = {}
            self.state_change_enabled = True

    def __init__(self):
        self.all_allowed_aliases = [self.DEFAULT_DB] + self._get_setting('database_slaves')
        self.reset()

    def get_all_allowed_aliases(self):
        """
        An explicit getter for `self.all_allowed_aliases` to play more nicely
        with `.utils.Routers`.
        """
        return self.all_allowed_aliases

    def _get_alive_database(self, db_choices, fallback):
        """ Helper to find a database that is alive """
        for db_name in db_choices:
            if self.is_alive(db_name):
                return db_name
        return fallback

    def _get_actual_master(self, model, **kwargs):
        return self.DEFAULT_DB

    def _get_possible_slaves(self, **kwargs):
        return shuffled(self._get_setting('database_slaves'))

    def _get_actual_slave(self, model, **kwargs):
        possible_slaves = self._get_possible_slaves(model=model, **kwargs)
        # Fallback to the db itself without even checking.
        return self._get_alive_database(possible_slaves, fallback=self.DEFAULT_DB)

    def reset(self):
        self._context = self.Context()

    @property
    def context(self):
        if self._context is None:
            self.reset()
        return self._context

    def init(self, state):
        self.reset()
        self.use_state(state)

    def is_alive(self, db_name, **kwargs):
        if not self._get_setting('check_is_alive'):
            return True

        from .dbchecker import db_is_alive

        return db_is_alive(db_name, cache_seconds=self._get_setting('database_downtime'))

    def set_state_change(self, enabled):
        self.context.state_change_enabled = enabled

    def state(self, default='master'):
        """
        Current state of routing, e.g. 'master' or 'slave'.
        """
        try:
            return self.context.state_stack[-1]
        except IndexError:
            return default

    def use_state(self, state):
        """
        Switch router into a new state.

        WARNING: Requires a paired call to 'revert' for reverting to the
        previous state.
        """
        if not self.context.state_change_enabled:
            state = self.state()
        self.context.state_stack.append(state)
        return self

    def revert(self):
        """
        Reverts wrapper state to a previous value after calling 'use_state'.
        """
        self.context.state_stack.pop()

    def db_for_write(self, model=None, **hints):
        state = self.state()
        if state == 'slave':  # `not in ('master', 'master_forced')` with the default middleware.
            if self._get_setting('check_state_on_write'):
                raise RuntimeError('Trying to access master database in slave state')
            # Otherwise: see below.

        # Tricky point: context is not read here, but saved, and it is shared
        # for reading and writing. Because of this, reading-after-writing leads
        # to the master database.
        chosen = self._get_actual_master(model, **hints)
        self.context.chosen[state] = chosen
        log.debug('db_for_write: %s', chosen)
        return chosen

    def db_for_read(self, model=None, **hints):
        state = self.state()
        if state != 'slave':
            return self.db_for_write(model, **hints)

        # Caching
        try:
            return self.context.chosen[state]
        except KeyError:
            pass

        chosen = self._get_actual_slave(model, **hints)
        self.context.chosen[state] = chosen
        log.debug('db_for_read: %s', chosen)
        return chosen

    def allow_relation(self, obj1, obj2, **hints):
        for db in (obj1._state.db, obj2._state.db):
            if db is not None and db not in self.all_allowed_aliases:
                return False
        return True


class ReplicationRouter(ReplicationRouterBase):
    """ A 'default' instance that initializes itself from django settings """

    def __init__(self):
        from django.conf import settings
        self._update_from_settings(settings)
        super(ReplicationRouter, self).__init__()
