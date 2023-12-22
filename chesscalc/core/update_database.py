# update_database.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""This module provides functions to update a database."""

from . import performancerecord
from . import filespec


def insert_record(
    database,
    rule,
    identity,
    player_name,
    from_date,
    to_date,
    event_list,
):
    """Insert record for rule, and details, into database.

    Return True if record is inserted and False otherwise.

    """
    if not database:
        return False
    if not rule:
        return False
    if (identity and event_list) or (not identity and not event_list):
        return False
    if (from_date and not to_date) or (not from_date and to_date):
        return False
    record = performancerecord.SelectorDBrecord()
    value = record.value
    value.name = rule
    value.from_date = from_date
    value.to_date = to_date
    value.person_identity = identity
    value.event_names.extend(event_list)
    record.key.recno = None
    database.start_transaction()
    try:
        record.put_record(database, filespec.SELECTION_FILE_DEF)
    except:
        database.backout()
        raise
    database.commit()
    return True
