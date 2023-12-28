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
    record.load_record(selection[0])
    database.start_read_only_transaction()
    try:
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


def get_events(tab, selection, database):
    """Populate tab with database values from events in selection."""
    if not tab or not selection or not database:
        return
