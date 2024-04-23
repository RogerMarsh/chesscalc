# identify_event.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Functions to update event identification on database.

The functions support identifying an event as an existing event on the
database, or as separate event, and undoing these identifications too.

"""
from . import eventrecord
from . import filespec
from . import identify_item


def identify(database, bookmarks, selection, answer):
    """Make bookmarked events aliases of selection event on database.

    The bookmarked events must not be aliases already.

    The selection event can be aliased already.

    The changes are applied to database.

    """
    answer["message"] = identify_item.identify(
        database,
        bookmarks,
        selection,
        eventrecord.EventDBvalue,
        eventrecord.EventDBrecord,
        filespec.EVENT_FILE_DEF,
        filespec.EVENT_FIELD_DEF,
        filespec.EVENT_ALIAS_FIELD_DEF,
        filespec.EVENT_IDENTITY_FIELD_DEF,
        "event",
    )


def break_bookmarked_aliases(database, bookmarks, selection, answer):
    """Break aliases of selection event in bookmarks on database.

    The bookmarked aliases of selection become separate events.

    The changes are applied to database.

    """
    answer["message"] = identify_item.break_bookmarked_aliases(
        database,
        bookmarks,
        selection,
        eventrecord.EventDBvalue,
        eventrecord.EventDBrecord,
        filespec.EVENT_FILE_DEF,
        filespec.EVENT_FIELD_DEF,
        filespec.EVENT_ALIAS_FIELD_DEF,
        filespec.EVENT_IDENTITY_FIELD_DEF,
        "event",
    )


def split_aliases(database, selection, answer):
    """Split aliases of selection event into separate events on database.

    The changes are applied to database.

    """
    answer["message"] = identify_item.split_aliases(
        database,
        selection,
        eventrecord.EventDBvalue,
        eventrecord.EventDBrecord,
        filespec.EVENT_FILE_DEF,
        filespec.EVENT_FIELD_DEF,
        filespec.EVENT_ALIAS_FIELD_DEF,
        filespec.EVENT_IDENTITY_FIELD_DEF,
        "event",
    )


def change_aliases(database, selection, answer):
    """Change alias of all events with same alias as selection on database.

    All events with same alias as selection have their alias changed to
    identity of selection event.

    The changes are applied to database.

    """
    answer["message"] = identify_item.change_aliases(
        database,
        selection,
        eventrecord.EventDBvalue,
        eventrecord.EventDBrecord,
        filespec.EVENT_FILE_DEF,
        filespec.EVENT_FIELD_DEF,
        filespec.EVENT_ALIAS_FIELD_DEF,
        filespec.EVENT_IDENTITY_FIELD_DEF,
        "event",
    )
