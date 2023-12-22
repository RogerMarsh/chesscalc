# identity.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide a unique identifier for each player record."""

from . import performancerecord
from . import constants
from . import filespec


class NoPlayerIdentity(Exception):
    """Raise if unable to allocate player identity code."""


class NoEventIdentity(Exception):
    """Raise if unable to allocate event identity code."""


class NoTimeIdentity(Exception):
    """Raise if unable to allocate time limit identity code."""


class NoModeIdentity(Exception):
    """Raise if unable to allocate playing mode identity code."""


def _create_identity_record_if_not_exists(database, key_type):
    """Create record for next identity if it does not exist."""
    database.start_read_only_transaction()
    if database.recordlist_key(
        filespec.IDENTITY_FILE_DEF,
        filespec.IDENTITY_TYPE_FIELD_DEF,
        key=database.encode_record_selector(key_type),
    ).count_records():
        database.end_read_only_transaction()
        return
    database.end_read_only_transaction()
    record = performancerecord.IdentityDBrecord()
    record.value.code = 0
    record.value.type_ = key_type
    database.start_transaction()
    record.put_record(database, filespec.IDENTITY_FILE_DEF)
    database.commit()


def create_player_identity_record_if_not_exists(database):
    """Delegate to _create_identity_record_if_not_exists for players."""
    _create_identity_record_if_not_exists(
        database, constants.PLAYER_IDENTITY_KEY
    )


def create_event_identity_record_if_not_exists(database):
    """Delegate to _create_identity_record_if_not_exists for events."""
    _create_identity_record_if_not_exists(
        database, constants.EVENT_IDENTITY_KEY
    )


def create_time_limit_identity_record_if_not_exists(database):
    """Delegate to _create_identity_record_if_not_exists for time limits."""
    _create_identity_record_if_not_exists(
        database, constants.TIME_IDENTITY_KEY
    )


def create_playing_mode_identity_record_if_not_exists(database):
    """Delegate to _create_identity_record_if_not_exists for playing modes."""
    _create_identity_record_if_not_exists(
        database, constants.MODE_IDENTITY_KEY
    )


def _get_next_identity_value_after_allocation(database, keytype, exception):
    """Allocate and return next identity code for keytype.

    Raise exception if next identity cannot be allocated.

    """
    recordlist = database.recordlist_key(
        filespec.IDENTITY_FILE_DEF,
        filespec.IDENTITY_TYPE_FIELD_DEF,
        key=database.encode_record_selector(keytype),
    )
    count = recordlist.count_records()
    if count == 0:
        raise exception("Identity code cannot be allocated")
    if count > 1:
        raise exception("Duplicate identity codes available")
    cursor = database.database_cursor(
        filespec.IDENTITY_FILE_DEF,
        filespec.IDENTITY_FIELD_DEF,
        recordset=recordlist,
    )
    record = performancerecord.IdentityDBrecord(
        valueclass=performancerecord.NextIdentityDBvalue
    )
    instance = cursor.first()
    if not instance:
        raise exception("Identity code record expected but not found")
    record.load_record(instance)
    new_record = record.clone()
    value = new_record.value
    if value.type_ != keytype:
        raise exception("Record is not the correct identity code type")
    value.code += 1

    # None is safe because self.srkey == new_record.srkey.
    record.edit_record(database, filespec.IDENTITY_FILE_DEF, None, new_record)

    # Plain value.code, an int object, is acceptable in sqlite3 but str(...)
    # is necessary for berkeleydb, lmdb, and others.
    return str(value.code)


def get_next_player_identity_value_after_allocation(database):
    """Allocate and return next player identity code.

    Raise NoPlayerIdentity if next identity cannot be allocated.

    """
    return _get_next_identity_value_after_allocation(
        database, constants.PLAYER_IDENTITY_KEY, NoPlayerIdentity
    )


def get_next_event_identity_value_after_allocation(database):
    """Allocate and return next event identity code.

    Raise NoEventIdentity if next identity cannot be allocated.

    """
    return _get_next_identity_value_after_allocation(
        database, constants.EVENT_IDENTITY_KEY, NoEventIdentity
    )


def get_next_timelimit_identity_value_after_allocation(database):
    """Allocate and return next time control identity code.

    Raise NoTimeIdentity if next identity cannot be allocated.

    """
    return _get_next_identity_value_after_allocation(
        database, constants.TIME_IDENTITY_KEY, NoTimeIdentity
    )


def get_next_mode_identity_value_after_allocation(database):
    """Allocate and return next playing mode identity code.

    Raise NoModeIdentity if next identity cannot be allocated.

    """
    return _get_next_identity_value_after_allocation(
        database, constants.MODE_IDENTITY_KEY, NoModeIdentity
    )
