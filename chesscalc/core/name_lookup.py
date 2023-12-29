# name_lookup.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""This module provides functions to translate identities to names.

The names must be suitable as the text of a tkinter.ttk.Entry widget.
"""

from . import performancerecord
from . import filespec


def get_player_name_from_identity(database, identity):
    """Return player name for identity or None."""
    person_record = None
    database.start_read_only_transaction()
    try:
        person_record = get_player_record_from_identity(database, identity)
    finally:
        database.end_read_only_transaction()
    if person_record is None:
        return None
    return person_record.value.alias_index_key()


def get_player_record_from_identity(database, identity):
    """Return player record for identity or None."""
    person_record = performancerecord.PlayerDBrecord()
    found = False
    recordlist = database.recordlist_key(
        filespec.PLAYER_FILE_DEF,
        filespec.PLAYER_IDENTITY_FIELD_DEF,
        key=database.encode_record_selector(identity),
    )
    while True:
        record = recordlist.next()
        if not record:
            break
        assert found is False
        found = True
        primary_record = database.get_primary_record(
            filespec.PLAYER_FILE_DEF, record[0]
        )
        person_record.load_record(primary_record)
    if not found:
        return None
    return person_record


def get_time_control_name_from_identity(database, identity):
    """Return time control name for identity or None."""
    time_control_record = None
    database.start_read_only_transaction()
    try:
        time_control_record = get_time_control_record_from_identity(
            database, identity
        )
    finally:
        database.end_read_only_transaction()
    if time_control_record is None:
        return None
    return time_control_record.value.alias_index_key()


def get_time_control_record_from_identity(database, identity):
    """Return time control record for identity or None."""
    time_control_record = performancerecord.TimeControlDBrecord()
    found = False
    recordlist = database.recordlist_key(
        filespec.TIME_FILE_DEF,
        filespec.TIME_IDENTITY_FIELD_DEF,
        key=database.encode_record_selector(identity),
    )
    while True:
        record = recordlist.next()
        if not record:
            break
        assert found is False
        found = True
        primary_record = database.get_primary_record(
            filespec.TIME_FILE_DEF, record[0]
        )
        time_control_record.load_record(primary_record)
    if not found:
        return None
    return time_control_record


def get_mode_name_from_identity(database, identity):
    """Return mode name for identity or None."""
    mode_record = None
    database.start_read_only_transaction()
    try:
        mode_record = get_mode_record_from_identity(
            database, identity
        )
    finally:
        database.end_read_only_transaction()
    if mode_record is None:
        return None
    return mode_record.value.alias_index_key()


def get_mode_record_from_identity(database, identity):
    """Return mode record for identity or None."""
    mode_record = performancerecord.ModeDBrecord()
    found = False
    recordlist = database.recordlist_key(
        filespec.MODE_FILE_DEF,
        filespec.MODE_IDENTITY_FIELD_DEF,
        key=database.encode_record_selector(identity),
    )
    while True:
        record = recordlist.next()
        if not record:
            break
        assert found is False
        found = True
        primary_record = database.get_primary_record(
            filespec.MODE_FILE_DEF, record[0]
        )
        mode_record.load_record(primary_record)
    if not found:
        return None
    return mode_record


def get_event_name_from_identity(database, identity):
    """Return event name for identity or None."""
