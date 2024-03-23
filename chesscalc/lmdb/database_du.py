# database_du.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess performance database deferred update using Symas LMDB via lmdb."""

from solentware_base import lmdbdu_database
from solentware_base import lmdb_database

from ..shared import litedu
from ..shared import alldu


class LmdbDatabaseduError(Exception):
    """Exception class for lmdb.database_du module."""


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


class Database(alldu.Alldu, litedu.Litedu, lmdbdu_database.Database):
    """Provide custom deferred update for chess performance database."""

    def __init__(self, DBfile, **kargs):
        """Delegate with LmdbDatabaseduError as exception class."""
        super().__init__(DBfile, LmdbDatabaseduError, **kargs)

        # Assume DEFAULT_MAP_PAGES * 100 is enough for adding 64000 normal
        # sized games: the largest segment size holds 64000 games and a
        # commit is done after every segment.
        self._set_map_blocks_above_used_pages(100)

    def deferred_update_housekeeping(self):
        """Override to check map size and pages used expected page usage.

        The checks are done here because housekeeping happens when segments
        become full, a convenient point for commit and database resize.

        """
        self._set_map_size_above_used_pages_between_transactions(100)


class DatabaseSU(alldu.Alldu, litedu.Litedu, lmdb_database.Database):
    """Provide custom deferred update for chess performance database."""

    def __init__(self, DBfile, **kargs):
        """Delegate with LmdbDatabaseduError as exception class."""
        super().__init__(DBfile, LmdbDatabaseduError, **kargs)

        # Assume DEFAULT_MAP_PAGES * 100 is enough for adding 64000 normal
        # sized games: the largest segment size holds 64000 games and a
        # commit is done after every segment.
        self._set_map_blocks_above_used_pages(100)

    def deferred_update_housekeeping(self):
        """Override to check map size and pages used expected page usage.

        The checks are done here because housekeeping happens when segments
        become full, a convenient point for commit and database resize.

        """
        self._set_map_size_above_used_pages_between_transactions(100)
