# identify_mode.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Functions to update mode identification on database.

The modes are ways of conducting the game, such as 'over the board' (OTB)
or 'online'.

The functions support identifying a mode as an existing mode
on the database, or as separate mode, and undoing these
identifications too.

"""
from ast import literal_eval

from . import performancerecord
from . import constants
from . import filespec


class ModeIdentity(Exception):
    """Raise if unable to change alias used as mode identity."""


def identify(database, bookmarks, selection):
    """Make bookmarked modes aliases of selection mode.

    The bookmarked modes must not be aliases already.

    The selection mode can be aliased already.

    The changes are applied to database.

    """
    mode_record = performancerecord.ModeDBrecord()
    selection_record = performancerecord.ModeDBrecord()
    database.start_transaction()
    try:
        selection_record.load_record(
            database.get_primary_record(
                filespec.MODE_FILE_DEF, selection[0][1]
            )
        )
        for event in bookmarks:
            mode_record.load_record(
                database.get_primary_record(filespec.MODE_FILE_DEF, event[1])
            )
            if mode_record.value.alias != mode_record.value.identity:
                database.backout()
                return "".join(
                    (
                        "One of the bookmarked modes is already ",
                        "aliased so no changes done",
                    )
                )
            clone_record = mode_record.clone()
            clone_record.value.alias = selection_record.value.alias
            mode_record.edit_record(
                database,
                filespec.MODE_FILE_DEF,
                filespec.MODE_IDENTITY_FIELD_DEF,
                clone_record,
            )
    except:
        database.backout()
        raise
    database.commit()
    return None


def break_bookmarked_aliases(database, bookmarks, selection):
    """Break aliases of selection mode in bookmarks.

    The bookmarked aliases of selection become separate modes.

    The changes are applied to database.

    """
    mode_record = performancerecord.ModeDBrecord()
    selection_record = performancerecord.ModeDBrecord()
    database.start_transaction()
    try:
        selection_record.load_record(
            database.get_primary_record(
                filespec.MODE_FILE_DEF, selection[0][1]
            )
        )
        for event in bookmarks:
            mode_record.load_record(
                database.get_primary_record(filespec.MODE_FILE_DEF, event[1])
            )
            if mode_record.value.alias != selection_record.value.alias:
                database.backout()
                return "".join(
                    (
                        "One of the bookmarked modes is not aliased ",
                        "to same mode as selection mode ",
                        "so no changes done",
                    )
                )
            clone_record = mode_record.clone()
            clone_record.value.alias = clone_record.value.identity
            mode_record.edit_record(
                database,
                filespec.MODE_FILE_DEF,
                filespec.MODE_IDENTITY_FIELD_DEF,
                clone_record,
            )
    except:
        database.backout()
        raise
    database.commit()
    return None


def split_aliases(database, selection):
    """Split aliases of selection mode into separate modes.

    The changes are applied to database.

    """
    mode_record = performancerecord.ModeDBrecord()
    selection_record = performancerecord.ModeDBrecord()
    database.start_transaction()
    try:
        selection_record.load_record(
            database.get_primary_record(
                filespec.MODE_FILE_DEF, selection[0][1]
            )
        )
        recordlist = database.recordlist_key(
            filespec.MODE_FILE_DEF,
            filespec.MODE_IDENTITY_FIELD_DEF,
            key=selection_record.value.alias,
        )
        while True:
            record = recordlist.next()
            if not record:
                break
            mode_record.load_record(
                database.get_primary_record(filespec.MODE_FILE_DEF, record[1])
            )
            if mode_record.value.alias == mode_record.value.identity:
                continue
            clone_record = mode_record.clone()
            clone_record.value.alias = clone_record.value.identity
            mode_record.edit_record(
                database,
                filespec.MODE_FILE_DEF,
                filespec.MODE_IDENTITY_FIELD_DEF,
                clone_record,
            )
    except:
        database.backout()
        raise
    database.commit()
    return None


def change_aliases(database, selection):
    """Change alias of all modes with same alias as selection.

    All modes with same alias as selection have their alias changed
    to identity of selection mode.

    The changes are applied to database.

    """
    mode_record = performancerecord.ModeDBrecord()
    selection_record = performancerecord.ModeDBrecord()
    database.start_transaction()
    try:
        selection_record.load_record(
            database.get_primary_record(
                filespec.MODE_FILE_DEF, selection[0][1]
            )
        )
        recordlist = database.recordlist_key(
            filespec.MODE_FILE_DEF,
            filespec.MODE_IDENTITY_FIELD_DEF,
            key=selection_record.value.alias,
        )
        while True:
            record = recordlist.next()
            if not record:
                break
            mode_record.load_record(
                database.get_primary_record(filespec.MODE_FILE_DEF, record[1])
            )
            clone_record = mode_record.clone()
            clone_record.value.alias = selection_record.value.identity
            mode_record.edit_record(
                database,
                filespec.MODE_FILE_DEF,
                filespec.MODE_IDENTITY_FIELD_DEF,
                clone_record,
            )
    except:
        database.backout()
        raise
    database.commit()
    return None


def _set_value(value, alias):
    """Populate value from alias.

    value is expected to be a ModeDBvalue instance.

    """
    (value.mode,) = literal_eval(alias)
