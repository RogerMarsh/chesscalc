# database_du.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess performance deferred update using Berkeley DB via tkinter."""

from solentware_base import db_tkinterdu_database
from solentware_base import db_tkinter_database

from ..shared import dbdu
from ..shared import alldu


class DbtkinterDatabaseduError(Exception):
    """Exception class for db_tkinter.database_du module."""


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


class Database(alldu.Alldu, dbdu.Dbdu, db_tkinterdu_database.Database):
    """Provide custom deferred update for chess performance database."""

    def __init__(self, DBfile, **kargs):
        """Delegate with DbtkinterDatabaseduError as exception class."""
        super().__init__(
            DBfile,
            DbtkinterDatabaseduError,
            ("-create", "-recover", "-txn", "-private", "-system_mem"),
            **kargs
        )


class DatabaseSU(alldu.Alldu, dbdu.Dbdu, db_tkinter_database.Database):
    """Provide custom deferred update for chess performance database."""

    def __init__(self, DBfile, **kargs):
        """Delegate with DbtkinterDatabaseduError as exception class."""
        super().__init__(
            DBfile,
            DbtkinterDatabaseduError,
            ("-create", "-recover", "-txn", "-private", "-system_mem"),
            **kargs
        )
