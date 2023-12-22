# identify_timecontrol.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Functions to update time control identification on database.

The functions support identifying a time control as an existing time control
on the database, or as separate time control, and undoing these
identifications too.

"""
from ast import literal_eval

from . import performancerecord
from . import constants
from . import filespec


class TimeControlIdentity(Exception):
    """Raise if unable to change alias used as time control identity."""


def identify(database, bookmarks, selection):
    """Make bookmarked time controls aliases of selection time control.

    The bookmarked time controls must not be aliases already.

    The selection time control can be aliased already.

    The changes are applied to database.

    """
    time_record = performancerecord.TimeControlDBrecord()
    selection_record = performancerecord.TimeControlDBrecord()
    database.start_transaction()
    try:
        selection_record.load_record(
            database.get_primary_record(
                filespec.TIME_FILE_DEF, selection[0][1]
            )
        )
        for event in bookmarks:
            time_record.load_record(
                database.get_primary_record(
                    filespec.TIME_FILE_DEF, event[1]
                )
            )
            if time_record.value.alias != time_record.value.identity:
                database.backout()
                return "".join(
                    (
                        "One of the bookmarked time controls is already ",
                        "aliased so no changes done",
                    )
                )
            clone_record = time_record.clone()
            clone_record.value.alias = selection_record.value.alias
            time_record.edit_record(
                database,
                filespec.TIME_FILE_DEF,
                filespec.TIME_IDENTITY_FIELD_DEF,
                clone_record,
            )
    except:
        database.backout()
        raise
    database.commit()
    return None


def break_bookmarked_aliases(database, bookmarks, selection):
    """Break aliases of selection time control in bookmarks.

    The bookmarked aliases of selection become separate time controls.

    The changes are applied to database.

    """
    time_record = performancerecord.TimeControlDBrecord()
    selection_record = performancerecord.TimeControlDBrecord()
    database.start_transaction()
    try:
        selection_record.load_record(
            database.get_primary_record(
                filespec.TIME_FILE_DEF, selection[0][1]
            )
        )
        for event in bookmarks:
            time_record.load_record(
                database.get_primary_record(
                    filespec.TIME_FILE_DEF, event[1]
                )
            )
            if time_record.value.alias != selection_record.value.alias:
                database.backout()
                return "".join(
                    (
                        "One of the bookmarked time controls is not aliased ",
                        "to same time control as selection time control ",
                        "so no changes done",
                    )
                )
            clone_record = time_record.clone()
            clone_record.value.alias = clone_record.value.identity
            time_record.edit_record(
                database,
                filespec.TIME_FILE_DEF,
                filespec.TIME_IDENTITY_FIELD_DEF,
                clone_record,
            )
    except:
        database.backout()
        raise
    database.commit()
    return None


def split_aliases(database, selection):
    """Split aliases of selection time control into separate time controls.

    The changes are applied to database.

    """
    time_record = performancerecord.TimeControlDBrecord()
    selection_record = performancerecord.TimeControlDBrecord()
    database.start_transaction()
    try:
        selection_record.load_record(
            database.get_primary_record(
                filespec.TIME_FILE_DEF, selection[0][1]
            )
        )
        recordlist = database.recordlist_key(
            filespec.TIME_FILE_DEF,
            filespec.TIME_IDENTITY_FIELD_DEF,
            key=selection_record.value.alias,
        )
        while True:
            record = recordlist.next()
            if not record:
                break
            time_record.load_record(
                database.get_primary_record(
                    filespec.TIME_FILE_DEF, record[1]
                )
            )
            if time_record.value.alias == time_record.value.identity:
                continue
            clone_record = time_record.clone()
            clone_record.value.alias = clone_record.value.identity
            time_record.edit_record(
                database,
                filespec.TIME_FILE_DEF,
                filespec.TIME_IDENTITY_FIELD_DEF,
                clone_record,
            )
    except:
        database.backout()
        raise
    database.commit()
    return None


def change_aliases(database, selection):
    """Change alias of all time controls with same alias as selection.

    All time controls with same alias as selection have their alias changed to
    identity of selection time control.

    The changes are applied to database.

    """
    time_record = performancerecord.TimeControlDBrecord()
    selection_record = performancerecord.TimeControlDBrecord()
    database.start_transaction()
    try:
        selection_record.load_record(
            database.get_primary_record(
                filespec.TIME_FILE_DEF, selection[0][1]
            )
        )
        recordlist = database.recordlist_key(
            filespec.TIME_FILE_DEF,
            filespec.TIME_IDENTITY_FIELD_DEF,
            key=selection_record.value.alias,
        )
        while True:
            record = recordlist.next()
            if not record:
                break
            time_record.load_record(
                database.get_primary_record(
                    filespec.TIME_FILE_DEF, record[1]
                )
            )
            clone_record = time_record.clone()
            clone_record.value.alias = selection_record.value.identity
            time_record.edit_record(
                database,
                filespec.TIME_FILE_DEF,
                filespec.TIME_IDENTITY_FIELD_DEF,
                clone_record,
            )
    except:
        database.backout()
        raise
    database.commit()
    return None


def _set_value(value, alias):
    """Populate value from alias.

    value is expected to be a TimeControlDBvalue instance.

    """
    (
        value.timecontrol,
    ) = literal_eval(alias)
