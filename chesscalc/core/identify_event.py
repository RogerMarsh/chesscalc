# identify_event.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Functions to update event identification on database.

The functions support identifying an event as an existing event on the
database, or as separate event, and undoing these identifications too.

"""
from ast import literal_eval

from . import performancerecord
from . import constants
from . import filespec


class EventIdentity(Exception):
    """Raise if unable to change alias used as event identity."""


def identify(database, bookmarks, selection):
    """Make bookmarked events aliases of selection event on database.

    The bookmarked events must not be aliases already.

    The selection event can be aliased already.

    The changes are applied to database.

    """
    event_record = performancerecord.EventDBrecord()
    selection_record = performancerecord.EventDBrecord()
    database.start_transaction()
    try:
        selection_record.load_record(
            database.get_primary_record(
                filespec.EVENT_FILE_DEF, selection[0][1]
            )
        )
        for event in bookmarks:
            event_record.load_record(
                database.get_primary_record(
                    filespec.EVENT_FILE_DEF, event[1]
                )
            )
            if event_record.value.alias != event_record.value.identity:
                database.backout()
                return "".join(
                    (
                        "One of the bookmarked events is already aliased ",
                        "so no changes done",
                    )
                )
            clone_record = event_record.clone()
            clone_record.value.alias = selection_record.value.alias
            event_record.edit_record(
                database,
                filespec.EVENT_FILE_DEF,
                filespec.EVENT_IDENTITY_FIELD_DEF,
                clone_record,
            )
    except:
        database.backout()
        raise
    database.commit()
    return None


def break_bookmarked_aliases(database, bookmarks, selection):
    """Break aliases of selection event in bookmarks on database.

    The bookmarked aliases of selection become separate events.

    The changes are applied to database.

    """
    event_record = performancerecord.EventDBrecord()
    selection_record = performancerecord.EventDBrecord()
    database.start_transaction()
    try:
        selection_record.load_record(
            database.get_primary_record(
                filespec.EVENT_FILE_DEF, selection[0][1]
            )
        )
        for event in bookmarks:
            event_record.load_record(
                database.get_primary_record(
                    filespec.EVENT_FILE_DEF, event[1]
                )
            )
            if event_record.value.alias != selection_record.value.alias:
                database.backout()
                return "".join(
                    (
                        "One of the bookmarked events is not aliased ",
                        "to same event as selection event ",
                        "so no changes done",
                    )
                )
            clone_record = event_record.clone()
            clone_record.value.alias = clone_record.value.identity
            event_record.edit_record(
                database,
                filespec.EVENT_FILE_DEF,
                filespec.EVENT_IDENTITY_FIELD_DEF,
                clone_record,
            )
    except:
        database.backout()
        raise
    database.commit()
    return None


def split_aliases(database, selection):
    """Split aliases of selection event into separate events on database.

    The changes are applied to database.

    """
    event_record = performancerecord.EventDBrecord()
    selection_record = performancerecord.EventDBrecord()
    database.start_transaction()
    try:
        selection_record.load_record(
            database.get_primary_record(
                filespec.EVENT_FILE_DEF, selection[0][1]
            )
        )
        recordlist = database.recordlist_key(
            filespec.EVENT_FILE_DEF,
            filespec.EVENT_IDENTITY_FIELD_DEF,
            key=selection_record.value.alias,
        )
        while True:
            record = recordlist.next()
            if not record:
                break
            event_record.load_record(
                database.get_primary_record(
                    filespec.EVENT_FILE_DEF, record[1]
                )
            )
            if event_record.value.alias == event_record.value.identity:
                continue
            clone_record = event_record.clone()
            clone_record.value.alias = clone_record.value.identity
            event_record.edit_record(
                database,
                filespec.EVENT_FILE_DEF,
                filespec.EVENT_IDENTITY_FIELD_DEF,
                clone_record,
            )
    except:
        database.backout()
        raise
    database.commit()
    return None


def change_aliases(database, selection):
    """Change alias of all events with same alias as selection on database.

    All events with same alias as selection have their alias changed to
    identity of selection event.

    The changes are applied to database.

    """
    event_record = performancerecord.EventDBrecord()
    selection_record = performancerecord.EventDBrecord()
    database.start_transaction()
    try:
        selection_record.load_record(
            database.get_primary_record(
                filespec.EVENT_FILE_DEF, selection[0][1]
            )
        )
        recordlist = database.recordlist_key(
            filespec.EVENT_FILE_DEF,
            filespec.EVENT_IDENTITY_FIELD_DEF,
            key=selection_record.value.alias,
        )
        while True:
            record = recordlist.next()
            if not record:
                break
            event_record.load_record(
                database.get_primary_record(
                    filespec.EVENT_FILE_DEF, record[1]
                )
            )
            clone_record = event_record.clone()
            clone_record.value.alias = selection_record.value.identity
            event_record.edit_record(
                database,
                filespec.EVENT_FILE_DEF,
                filespec.EVENT_IDENTITY_FIELD_DEF,
                clone_record,
            )
    except:
        database.backout()
        raise
    database.commit()
    return None


def _set_value(value, alias):
    """Populate value from alias.

    value is expected to be a EventDBvalue instance.

    """
    (
        value.event,
        value.eventdate,
        value.section,
        value.stage,
    ) = literal_eval(alias)
