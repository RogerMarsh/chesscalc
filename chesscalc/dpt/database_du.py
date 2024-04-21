# database_du.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess performance database deferred update using DPT via dpt."""

import os

from solentware_base import dptdu_database
from solentware_base import dpt_database
from solentware_base.core import constants as sb_core_constants

from ..shared import litedu
from ..shared import alldu


class DPTDatabaseduError(Exception):
    """Exception class for dpt.database_du module."""


def database_du(dbpath, *args, **kwargs):
    """Open database, import games and close database."""
    # sysfolder argument defaults to DPT_SYSDU_FOLDER in dptdu_database.
    alldu.do_deferred_update(
        Database(dbpath, allowcreate=True), *args, **kwargs
    )


def database_su(dbpath, *args, **kwargs):
    """Open database, import games without indexing, and close database."""
    alldu.do_deferred_update(
        DatabaseSU(
            dbpath,
            allowcreate=True,
            sysfolder=os.path.join(
                dbpath, sb_core_constants.DPT_SYSFUL_FOLDER
            ),
        ),
        *args,
        indexing=False,
        **kwargs,
    )


def games_du(dbpath, *args, **kwargs):
    """Open database, index games and close database."""
    alldu.do_games_deferred_update(
        DatabaseSU(
            dbpath,
            allowcreate=True,
            sysfolder=os.path.join(
                dbpath, sb_core_constants.DPT_SYSFUL_FOLDER
            ),
        ),
        *args,
        **kwargs,
    )


def players_su(dbpath, *args, **kwargs):
    """Open database, copy player names from games and close database."""
    alldu.do_players_deferred_update(
        DatabaseSU(
            dbpath,
            allowcreate=True,
            sysfolder=os.path.join(
                dbpath, sb_core_constants.DPT_SYSFUL_FOLDER
            ),
        ),
        *args,
        **kwargs,
    )


def events_su(dbpath, *args, **kwargs):
    """Open database, copy event names from games and close database."""
    alldu.do_events_deferred_update(
        DatabaseSU(
            dbpath,
            allowcreate=True,
            sysfolder=os.path.join(
                dbpath, sb_core_constants.DPT_SYSFUL_FOLDER
            ),
        ),
        *args,
        **kwargs,
    )


def time_controls_su(dbpath, *args, **kwargs):
    """Open database, copy time control names from games and close database."""
    alldu.do_time_controls_deferred_update(
        DatabaseSU(
            dbpath,
            allowcreate=True,
            sysfolder=os.path.join(
                dbpath, sb_core_constants.DPT_SYSFUL_FOLDER
            ),
        ),
        *args,
        **kwargs,
    )


def modes_su(dbpath, *args, **kwargs):
    """Open database, copy mode names from games and close database."""
    alldu.do_modes_deferred_update(
        DatabaseSU(
            dbpath,
            allowcreate=True,
            sysfolder=os.path.join(
                dbpath, sb_core_constants.DPT_SYSFUL_FOLDER
            ),
        ),
        *args,
        **kwargs,
    )


def terminations_su(dbpath, *args, **kwargs):
    """Open database, copy termination names from games and close database."""
    alldu.do_terminations_deferred_update(
        DatabaseSU(
            dbpath,
            allowcreate=True,
            sysfolder=os.path.join(
                dbpath, sb_core_constants.DPT_SYSFUL_FOLDER
            ),
        ),
        *args,
        **kwargs,
    )


def player_types_su(dbpath, *args, **kwargs):
    """Open database, copy player type names from games and close database."""
    alldu.do_player_types_deferred_update(
        DatabaseSU(
            dbpath,
            allowcreate=True,
            sysfolder=os.path.join(
                dbpath, sb_core_constants.DPT_SYSFUL_FOLDER
            ),
        ),
        *args,
        **kwargs,
    )


class Database(alldu.Alldu, litedu.Litedu, dptdu_database.Database):
    """Provide custom deferred update for chess performance database."""

    def __init__(self, databasefolder, **kargs):
        """Delegate with DPTDatabaseduError as exception class."""
        super().__init__(databasefolder, DPTDatabaseduError, **kargs)


class DatabaseSU(alldu.Alldu, litedu.Litedu, dpt_database.Database):
    """Provide custom deferred update for chess performance database."""

    def __init__(self, databasefolder, **kargs):
        """Delegate with DPTDatabaseduError as exception class."""
        super().__init__(databasefolder, DPTDatabaseduError, **kargs)
