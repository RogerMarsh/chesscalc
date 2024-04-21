# database_du.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess performance deferred update using Berkeley DB via berkeleydb."""

import berkeleydb.db

from solentware_base import berkeleydbdu_database
from solentware_base import berkeleydb_database

from ..shared import dbdu
from ..shared import alldu


class BerkeleydbDatabaseduError(Exception):
    """Exception class for berkeleydb.database_du module."""


def database_du(dbpath, *args, **kwargs):
    """Open database, import games and close database."""
    alldu.do_deferred_update(
        Database(dbpath, allowcreate=True), *args, **kwargs
    )


def database_su(dbpath, *args, **kwargs):
    """Open database, import games without indexing, and close database."""
    alldu.do_deferred_update(
        DatabaseSU(dbpath, allowcreate=True), *args, indexing=False, **kwargs
    )


def games_su(dbpath, *args, **kwargs):
    """Open database, index games and close database."""
    alldu.do_games_deferred_update(
        DatabaseSU(dbpath, allowcreate=True), *args, **kwargs
    )


def players_su(dbpath, *args, **kwargs):
    """Open database, copy player names from games and close database."""
    alldu.do_players_deferred_update(
        DatabaseSU(dbpath, allowcreate=True), *args, **kwargs
    )


def events_su(dbpath, *args, **kwargs):
    """Open database, copy event names from games and close database."""
    alldu.do_events_deferred_update(
        DatabaseSU(dbpath, allowcreate=True), *args, **kwargs
    )


def time_controls_su(dbpath, *args, **kwargs):
    """Open database, copy time control names from games and close database."""
    alldu.do_time_controls_deferred_update(
        DatabaseSU(dbpath, allowcreate=True), *args, **kwargs
    )


def modes_su(dbpath, *args, **kwargs):
    """Open database, copy mode names from games and close database."""
    alldu.do_modes_deferred_update(
        DatabaseSU(dbpath, allowcreate=True), *args, **kwargs
    )


def terminations_su(dbpath, *args, **kwargs):
    """Open database, copy termination names from games and close database."""
    alldu.do_terminations_deferred_update(
        DatabaseSU(dbpath, allowcreate=True), *args, **kwargs
    )


def player_types_su(dbpath, *args, **kwargs):
    """Open database, copy player type names from games and close database."""
    alldu.do_player_types_deferred_update(
        DatabaseSU(dbpath, allowcreate=True), *args, **kwargs
    )


class Database(alldu.Alldu, dbdu.Dbdu, berkeleydbdu_database.Database):
    """Provide custom deferred update for chess performance database."""

    def __init__(self, DBfile, **kargs):
        """Delegate with BerkeleydbDatabaseduError as exception class."""
        super().__init__(
            DBfile,
            BerkeleydbDatabaseduError,
            (
                berkeleydb.db.DB_CREATE
                | berkeleydb.db.DB_RECOVER
                | berkeleydb.db.DB_INIT_MPOOL
                | berkeleydb.db.DB_INIT_LOCK
                | berkeleydb.db.DB_INIT_LOG
                | berkeleydb.db.DB_INIT_TXN
                | berkeleydb.db.DB_PRIVATE
            ),
            **kargs
        )


class DatabaseSU(alldu.Alldu, dbdu.Dbdu, berkeleydb_database.Database):
    """Provide custom deferred update for chess performance database."""

    def __init__(self, DBfile, **kargs):
        """Delegate with BerkeleydbDatabaseduError as exception class."""
        super().__init__(
            DBfile,
            BerkeleydbDatabaseduError,
            (
                berkeleydb.db.DB_CREATE
                | berkeleydb.db.DB_RECOVER
                | berkeleydb.db.DB_INIT_MPOOL
                | berkeleydb.db.DB_INIT_LOCK
                | berkeleydb.db.DB_INIT_LOG
                | berkeleydb.db.DB_INIT_TXN
                | berkeleydb.db.DB_PRIVATE
            ),
            **kargs
        )

    # Class structure implies this is not an override at present.
    def deferred_update_housekeeping(self):
        """Override to do nothing."""
