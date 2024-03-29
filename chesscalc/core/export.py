# export.py
# Copyright 2024 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Prepare exports of player identifications on database.

Player identifications are chosen by selecting one or more players, or
by selecting one or more events and taking all the players in the events.

"""
import ast

from . import performancerecord
from . import filespec
from . import identify_item


class ExportPersonError(Exception):
    """Raise if unable to do export action on identified person."""


class ExportStatus:
    """Note status of an _Export.prepare_export_data() call.

    It is assumed a subclass of _Export defines prepare_export_data.
    """

    def __init__(self, error_message=None):
        """Note the error message."""
        self.error_message = error_message


class ImportRepr(Exception):
    """Raise if literal_eval does not give [[(), ()], [(), ()], ...]."""


class _Export:
    """Export persons from database."""

    def __init__(self, database):
        """Note the database."""
        self._database = database
        self.export_data = None
        self.error_message = None

    def export_repr(self):
        """Return repr of self.export_data."""
        return repr(self.export_data)


class _ExportSelected(_Export):
    """Export selected and bookmarked persons from database."""

    def __init__(self, database, selection, bookmarks):
        """Note the database, selection, and bookmarks."""
        super().__init__(database)
        self._selected = set(bookmarks + selection)


class ExportPersons(_ExportSelected):
    """Export selected and bookmarked persons from database."""

    def prepare_export_data(self):
        """Prepare dict of person identities for selected persons."""
        self.export_data = []
        export_data = self.export_data
        database = self._database
        encode_record_selector = database.encode_record_selector
        value = performancerecord.PersonDBvalue()
        person_record = performancerecord.PlayerDBrecord(
            valueclass=performancerecord.PersonDBvalue
        )
        database.start_read_only_transaction()
        try:
            exportedpersons = database.recordlist_nil(filespec.PLAYER_FILE_DEF)
            for item in self._selected:
                value.load_alias_index_key(item[0])
                selector = encode_record_selector(value.alias_index_key())
                itempersons = database.recordlist_key(
                    filespec.PLAYER_FILE_DEF,
                    filespec.PERSON_ALIAS_FIELD_DEF,
                    key=selector,
                )
                if (exportedpersons & itempersons).count_records():
                    continue
                try:
                    _export_aliases_of_person(
                        itempersons,
                        export_data,
                        exportedpersons,
                        database,
                        person_record,
                        value,
                    )
                except ExportPersonError as exc:
                    return ExportStatus(
                        error_message=_generate_exception_report(
                            exc, value.alias_index_key()
                        )
                    )
        finally:
            database.end_read_only_transaction()
        return ExportStatus()


class ExportEventPersons(_ExportSelected):
    """Export selected and bookmarked persons from database."""

    def prepare_export_data(self):
        """Prepare dict of person identities for selected events."""
        self.export_data = []
        export_data = self.export_data
        database = self._database
        encode_record_selector = database.encode_record_selector
        eventvalue = performancerecord.EventDBvalue()
        value = performancerecord.PersonDBvalue()
        gamevalue = performancerecord.GameDBvalue()
        person_record = performancerecord.PlayerDBrecord(
            valueclass=performancerecord.PersonDBvalue
        )
        database.start_read_only_transaction()
        try:
            exportedpersons = database.recordlist_nil(filespec.PLAYER_FILE_DEF)
            for item in self._selected:
                eventvalue.load_alias_index_key(item[0])
                selector = encode_record_selector(eventvalue.alias_index_key())
                itemevents = database.recordlist_key(
                    filespec.EVENT_FILE_DEF,
                    filespec.EVENT_ALIAS_FIELD_DEF,
                    key=selector,
                )
                count = itemevents.count_records()
                if count == 0:
                    return ExportStatus(
                        error_message="Event record does not exist"
                    )
                if count > 1:
                    return ExportStatus(
                        error_message="Event record duplicated"
                    )
                itemgames = database.recordlist_key(
                    filespec.GAME_FILE_DEF,
                    filespec.GAME_EVENT_FIELD_DEF,
                    key=selector,
                )
                cursor = itemgames.create_recordsetbase_cursor()
                while True:
                    data = cursor.next()
                    if data is None:
                        break
                    gamevalue.load(data[1])
                    for player_alias in (
                        gamevalue.black_key(),
                        gamevalue.white_key(),
                    ):
                        selector = encode_record_selector(player_alias)
                        itempersons = database.recordlist_key(
                            filespec.PLAYER_FILE_DEF,
                            filespec.PERSON_ALIAS_FIELD_DEF,
                            key=selector,
                        )
                        if (exportedpersons & itempersons).count_records():
                            continue
                        try:
                            _export_aliases_of_person(
                                itempersons,
                                export_data,
                                exportedpersons,
                                database,
                                person_record,
                                value,
                            )
                        except ExportPersonError as exc:
                            return ExportStatus(
                                error_message=_generate_exception_report(
                                    exc, player_alias
                                )
                            )
        finally:
            database.end_read_only_transaction()
        return ExportStatus()


class ExportIdentities(_Export):
    """Export all person identities, but no aliases, from database."""

    def prepare_export_data(self):
        """Prepare list of person identities for all persons."""
        self.export_data = []
        export_data = self.export_data
        database = self._database
        value = performancerecord.PersonDBvalue()
        database.start_read_only_transaction()
        try:
            persons = database.recordlist_all(
                filespec.PLAYER_FILE_DEF, filespec.PERSON_ALIAS_FIELD_DEF
            )
            cursor = persons.create_recordsetbase_cursor()
            while True:
                data = cursor.next()
                if data is None:
                    break
                value.load(data[1])
                if value.alias == value.identity:
                    export_data.append(value.alias_index())
        finally:
            database.end_read_only_transaction()


def _generate_exception_report(exc, key):
    """Return str for exception exc raised for key."""
    return "\n\n".join(
        (str(exc), "\n".join(str(s) for s in ast.literal_eval(key)))
    )


def _export_aliases_of_person(
    itempersons,
    export_data,
    exportedpersons,
    database,
    person_record,
    value,
):
    """Copy aliases of persons for export and mark as processed.

    itempersons list has a reference to the person to add to the export.
    export_data is the (Python) list where the person's references are put.
    exportedpersons list is where the processed references are put.
    the other arguments are helpers to avoid re-creating temporary objects.

    """
    count = itempersons.count_records()
    if count == 0:
        raise ExportPersonError("Person is not on known players list")
    if count > 1:
        raise ExportPersonError("Person record duplicated")
    itemdata = identify_item.get_first_item_on_recordlist(
        database,
        itempersons,
        filespec.PLAYER_FILE_DEF,
    )
    person_record.load_record(itemdata)
    itemaliases = database.recordlist_key(
        filespec.PLAYER_FILE_DEF,
        filespec.PLAYER_IDENTITY_FIELD_DEF,
        key=database.encode_record_selector(person_record.value.alias),
    )
    aliases = set()
    cursor = itemaliases.create_recordsetbase_cursor()
    while True:
        data = cursor.next()
        if data is None:
            break
        value.load(data[1])
        aliases.add(value.alias_index())
    exportedpersons |= itemaliases
    export_data.append(aliases)


def import_repr(value):
    """Return literal evaluation of value."""
    data = ast.literal_eval(value)
    if not isinstance(data, list):
        raise ImportRepr("Data is not a list")
    for item in data:
        if not isinstance(item, set):
            raise ImportRepr("Item in data is not a set")
        for person in item:
            if not isinstance(person, tuple):
                raise ImportRepr("Person in item in data is not a tuple")
            if len(person) != 7:
                raise ImportRepr("Length of person in item in data is not 7")
            for element in person:
                if element is not None and not isinstance(element, str):
                    raise ImportRepr(
                        "".join(
                            (
                                "Element of person in item in data is ",
                                "neither None nor a str",
                            )
                        )
                    )
    return data


def write_export_file(export_file, serialized_data):
    """Write serialized data to export file."""
    with open(export_file, "w", encoding="utf-8") as output:
        output.write(serialized_data)


def read_export_file(import_file):
    """Return serialized data read from inport file."""
    with open(import_file, "r", encoding="utf-8") as input_:
        return ast.literal_eval(input_.read())
