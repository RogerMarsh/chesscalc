# tab_from_selection.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""This module provides functions to populate a rule tab from a selection."""

from . import performancerecord
from . import filespec


def get_rule(tab, selection, database):
    """Populate tab with database values from rule in selection."""
    if not tab or not selection or not database:
        return
    record = performancerecord.SelectorDBrecord()
    database.start_read_only_transaction()
    try:
        record.load_record(
            database.get_primary_record(
                filespec.SELECTION_FILE_DEF, selection[0][1]
            )
        )
        tab.populate_rule_from_record(record)
    finally:
        database.end_read_only_transaction()
    return


def get_person(tab, selection, database):
    """Populate tab with database values from person in selection."""
    if not tab or not selection or not database:
        return
    database.start_read_only_transaction()
    try:
        tab.populate_rule_person_from_record(
            get_person_detail(selection[0][1], database)
        )
    finally:
        database.end_read_only_transaction()
    return


def get_person_detail(key, database):
    """Return record for person referenced by key in database."""
    record = performancerecord.PlayerDBrecord(
        valueclass=performancerecord.PersonDBvalue
    )
    record.load_record(
        database.get_primary_record(filespec.PLAYER_FILE_DEF, key)
    )
    return record


def get_events(tab, selection, bookmarks, database):
    """Populate tab from selected and bookmarked events in database."""
    if not tab or (not selection and not bookmarks) or not database:
        return
    eventset = set(bookmarks)
    if selection:
        eventset.add(selection[0])
    database.start_read_only_transaction()
    try:
        tab.populate_rule_events_from_records(
            get_event_details([bmk[1] for bmk in sorted(eventset)], database)
        )
    finally:
        database.end_read_only_transaction()
    return


def get_event_details(keys, database):
    """Return records for events referenced by keys in database."""
    records = []
    for key in keys:
        record = performancerecord.EventDBrecord()
        record.load_record(
            database.get_primary_record(filespec.EVENT_FILE_DEF, key)
        )
        records.append(record)
    return records


def get_time_control(tab, selection, database):
    """Populate tab with database values from time control in selection."""
    if not tab or not selection or not database:
        return
    database.start_read_only_transaction()
    try:
        tab.populate_rule_time_control_from_record(
            get_time_control_detail(selection[0][1], database)
        )
    finally:
        database.end_read_only_transaction()
    return


def get_time_control_detail(key, database):
    """Return record for time control referenced by key in database."""
    record = performancerecord.TimeControlDBrecord()
    record.load_record(
        database.get_primary_record(filespec.TIME_FILE_DEF, key)
    )
    return record


def get_mode(tab, selection, database):
    """Populate tab with database values from mode in selection."""
    if not tab or not selection or not database:
        return
    database.start_read_only_transaction()
    try:
        tab.populate_rule_mode_from_record(
            get_mode_detail(selection[0][1], database)
        )
    finally:
        database.end_read_only_transaction()
    return


def get_mode_detail(key, database):
    """Return record for mode referenced by key in database."""
    record = performancerecord.ModeDBrecord()
    record.load_record(
        database.get_primary_record(filespec.MODE_FILE_DEF, key)
    )
    return record
