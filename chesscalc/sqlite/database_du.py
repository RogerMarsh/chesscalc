# database_du.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess performance database deferred update using Sqlite 3 via sqlite3."""

from solentware_base import sqlite3du_database
from solentware_base import sqlite3_database

from ..shared import litedu
from ..shared import alldu


class Sqlite3DatabaseduError(Exception):
    """Exception class for sqlite.database_du module."""


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


class Database(alldu.Alldu, litedu.Litedu, sqlite3du_database.Database):
    """Provide custom deferred update for chess performance database."""

    def __init__(self, sqlite3file, **kargs):
        """Delegate with Sqlite3DatabaseduError as exception class."""
        super().__init__(sqlite3file, Sqlite3DatabaseduError, **kargs)


class DatabaseSU(alldu.Alldu, litedu.Litedu, sqlite3_database.Database):
    """Provide custom deferred update for chess performance database."""

    def __init__(self, sqlite3file, **kargs):
        """Delegate with Sqlite3DatabaseduError as exception class."""
        super().__init__(sqlite3file, Sqlite3DatabaseduError, **kargs)

    # Class structure implies this is not an override at present.
    def deferred_update_housekeeping(self):
        """Override to do nothing."""
