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
    event_list,
    time_control_identity,
    mode_identity,
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
    value.event_identities.extend(event_list)
    value.time_control_identity = time_control_identity
    value.mode_identity = mode_identity
    record.key.recno = None
    database.start_transaction()
    try:
        record.put_record(database, filespec.SELECTION_FILE_DEF)
    except:
        database.backout()
        raise
    database.commit()
    return True
