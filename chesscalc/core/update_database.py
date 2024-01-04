# update_database.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""This module provides functions to update a database."""

from . import performancerecord
from . import filespec


def insert_record(
    database,
    rule,
    player_identity,
    from_date,
    to_date,
    time_control_identity,
    mode_identity,
    event_list,
):
    """Insert record for rule, and details, into database.

    Return True if record is inserted and False otherwise.

    """
    if not database:
        return False
    if not rule:
        return False
    if (player_identity and event_list) or (
        not player_identity and not event_list
    ):
        return False
    if (from_date and not to_date) or (not from_date and to_date):
        return False
    record = performancerecord.SelectorDBrecord()
    value = record.value
    value.name = rule
    value.from_date = from_date
    value.to_date = to_date
    value.person_identity = player_identity
    value.time_control_identity = time_control_identity
    value.mode_identity = mode_identity
    value.event_identities.extend(event_list)
    record.key.recno = None
    database.start_transaction()
    try:
        record.put_record(database, filespec.SELECTION_FILE_DEF)
    except:  # pycodestyle E722: pylint is happy with following 'raise'.
        database.backout()
        raise
    database.commit()
    return True


def update_record(
    database,
    record,
    rule,
    player_identity,
    from_date,
    to_date,
    time_control_identity,
    mode_identity,
    event_list,
):
    """Update record for rule, and details, on database.

    Return True if record is updated and False otherwise.

    """
    if not database:
        return False
    if not record:
        return False
    assert isinstance(record, performancerecord.SelectorDBrecord)
    if not rule:
        return False
    if (player_identity and event_list) or (
        not player_identity and not event_list
    ):
        return False
    if (from_date and not to_date) or (not from_date and to_date):
        return False
    database.start_transaction()
    try:
        existing = database.get_primary_record(
            filespec.SELECTION_FILE_DEF, record.key.pack()
        )
        if existing is None:
            database.backout()
            return False
        dbrecord = performancerecord.SelectorDBrecord()
        dbrecord.load_record(existing)
        if dbrecord != record:
            database.backout()
            return False
        clone_record = dbrecord.clone()
        value = clone_record.value
        value.name = rule
        value.from_date = from_date
        value.to_date = to_date
        value.person_identity = player_identity
        value.time_control_identity = time_control_identity
        value.mode_identity = mode_identity
        value.event_identities.extend(event_list)
        assert dbrecord.srkey == clone_record.srkey
        dbrecord.edit_record(
            database, filespec.SELECTION_FILE_DEF, None, clone_record
        )
    except:  # pycodestyle E722: pylint is happy with following 'raise'.
        database.backout()
        raise
    database.commit()
    return True


def delete_record(database, record):
    """Delete record for rule from database.

    Return True if record is deleted and False otherwise.

    """
    if not database:
        return False
    if not record:
        return False
    assert isinstance(record, performancerecord.SelectorDBrecord)
    database.start_transaction()
    try:
        existing = database.get_primary_record(
            filespec.SELECTION_FILE_DEF, record.key.pack()
        )
        if existing is None:
            database.backout()
            return False
        dbrecord = performancerecord.SelectorDBrecord()
        dbrecord.load_record(existing)
        if dbrecord != record:
            database.backout()
            return False
        record.delete_record(database, filespec.SELECTION_FILE_DEF)
    except:  # pycodestyle E722: pylint is happy with following 'raise'.
        database.backout()
        raise
    database.commit()
    return True
