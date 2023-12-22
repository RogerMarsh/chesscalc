# database_du.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess performance database deferred update using Unqlite via unqlite."""

from solentware_base import unqlitedu_database
from solentware_base import unqlite_database

from ..shared import litedu
from ..shared import alldu


class UnqliteDatabaseduError(Exception):
    """Exception class for unqlite.database_du module."""


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


class Database(alldu.Alldu, litedu.Litedu, unqlitedu_database.Database):
    """Provide custom deferred update for chess performance database."""

    def __init__(self, unqlitefile, **kargs):
        """Delegate with UnqliteDatabaseduError as exception class."""
        super().__init__(unqlitefile, UnqliteDatabaseduError, **kargs)


class DatabaseSU(alldu.Alldu, litedu.Litedu, unqlite_database.Database):
    """Provide custom deferred update for chess performance database."""

    def __init__(self, unqlitefile, **kargs):
        """Delegate with UnqliteDatabaseduError as exception class."""
        super().__init__(unqlitefile, UnqliteDatabaseduError, **kargs)
