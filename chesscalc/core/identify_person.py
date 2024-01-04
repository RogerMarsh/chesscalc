# identify_person.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Functions to update player identification on database.

The functions support identifying a new player as an existing or new
person on the database, and undoing these identifications too.

"""
from . import performancerecord
from . import filespec
from . import identify_item


class PersonToPlayer(Exception):
    """Raise if unable to do split action on identified person."""


class PlayerToPerson(Exception):
    """Raise if unable to allocation player identity code."""


class PersonIdentity(Exception):
    """Raise if unable to change alias used as identified person."""


def identify_players_as_person(database, players, person):
    """Make new players aliases of identified person on database.

    If person is a new player rather than an identified person it is
    turned into an identified person.

    All players become aliases of person.

    The changes are applied to database.

    """
    value = performancerecord.PersonDBvalue()
    value.load_alias_index_key(person[0][0])
    selector = database.encode_record_selector(value.alias_index_key())
    database.start_transaction()
    try:
        recordlist = database.recordlist_key(
            filespec.PLAYER_FILE_DEF,
            filespec.PERSON_ALIAS_FIELD_DEF,
            key=selector,
        )
        count = recordlist.count_records()
        if count > 1:
            raise PlayerToPerson("Person record duplicated")
        if count == 1:
            person_record = performancerecord.PlayerDBrecord(
                valueclass=performancerecord.PersonDBvalue
            )
            person_record.load_record(
                identify_item.get_first_item_on_recordlist(
                    database,
                    recordlist,
                    filespec.PLAYER_FILE_DEF,
                    filespec.PLAYER_FIELD_DEF,
                )
            )
        else:
            recordlist = database.recordlist_key(
                filespec.PLAYER_FILE_DEF,
                filespec.PLAYER_ALIAS_FIELD_DEF,
                key=selector,
            )
            count = recordlist.count_records()
            if count == 0:
                raise PlayerToPerson("New person record does not exists")
            if count > 1:
                raise PlayerToPerson("New person record duplicated")
            primary_record = identify_item.get_first_item_on_recordlist(
                database,
                recordlist,
                filespec.PLAYER_FILE_DEF,
                filespec.PLAYER_FIELD_DEF,
            )
            player_record = performancerecord.PlayerDBrecord()
            player_record.load_record(primary_record)
            person_record = performancerecord.PlayerDBrecord(
                valueclass=performancerecord.PersonDBvalue
            )
            person_record.load_record(primary_record)

            # None is safe because self.srkey == new_record.srkey.
            # filespec.PLAYER_ALIAS_FIELD_DEF is correct value otherwise
            # because of how argument is used in edit_record().
            player_record.edit_record(
                database, filespec.PLAYER_FILE_DEF, None, person_record
            )

        alias = person_record.value.alias
        for player in players:
            # value should be PlayerDBvalue but while PersonDBvalue gives
            # the same answer there is no need to change it.
            value.load_alias_index_key(player[0])
            selector = database.encode_record_selector(value.alias_index_key())
            recordlist = database.recordlist_key(
                filespec.PLAYER_FILE_DEF,
                filespec.PLAYER_ALIAS_FIELD_DEF,
                key=selector,
            )
            count = recordlist.count_records()
            if count > 1:
                raise PlayerToPerson("Player record duplicated")
            if count == 0:
                raise PlayerToPerson("Player record does not exists")
            primary_record = identify_item.get_first_item_on_recordlist(
                database,
                recordlist,
                filespec.PLAYER_FILE_DEF,
                filespec.PLAYER_FIELD_DEF,
            )
            player_record = performancerecord.PlayerDBrecord()
            player_record.load_record(primary_record)
            person_record = performancerecord.PlayerDBrecord(
                valueclass=performancerecord.PersonDBvalue
            )
            person_record.load_record(primary_record)
            person_record.value.alias = alias

            # None is safe because self.srkey == new_record.srkey.
            # filespec.PLAYER_ALIAS_FIELD_DEF is correct value otherwise
            # because of how argument is used in edit_record().
            player_record.edit_record(
                database, filespec.PLAYER_FILE_DEF, None, person_record
            )

    except:  # pycodestyle E722: pylint is happy with following 'raise'.
        database.backout()
        raise
    database.commit()


def split_person_into_all_players(database, person):
    """Split person into new player aliases on database.

    All aliases of person become separate new players.

    The changes are applied to database.

    """
    value = performancerecord.PersonDBvalue()
    value.load_alias_index_key(person[0][0])
    selector = database.encode_record_selector(value.alias_index_key())
    database.start_transaction()
    try:
        recordlist = database.recordlist_key(
            filespec.PLAYER_FILE_DEF,
            filespec.PERSON_ALIAS_FIELD_DEF,
            key=selector,
        )
        count = recordlist.count_records()
        if count == 0:
            raise PersonToPlayer("Cannot split: person record does not exist")
        if count > 1:
            raise PersonToPlayer("Cannot split: person record duplicated")
        primary_record = identify_item.get_first_item_on_recordlist(
            database,
            recordlist,
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYER_FIELD_DEF,
        )
        person_record = performancerecord.PlayerDBrecord(
            valueclass=performancerecord.PersonDBvalue
        )
        person_record.load_record(primary_record)
        if person_record.value.identity != person_record.value.alias:
            database.backout()
            return "Cannot split: selection is not the identified person"
        identity = person_record.value.alias
        recordlist = database.recordlist_key(
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYER_IDENTITY_FIELD_DEF,
            key=database.encode_record_selector(identity),
        )
        count = recordlist.count_records()
        if count == 0:
            raise PlayerToPerson("Cannot split: no players with this identity")
        cursor = database.database_cursor(
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYER_FIELD_DEF,
            recordset=recordlist,
        )
        try:
            while True:
                record = cursor.next()
                if not record:
                    break
                primary_record = database.get_primary_record(
                    filespec.PLAYER_FILE_DEF, record[0]
                )
                alias_record = performancerecord.PlayerDBrecord(
                    valueclass=performancerecord.PersonDBvalue
                )
                alias_record.load_record(primary_record)
                if identity != alias_record.value.alias:
                    database.backout()
                    return "Cannot split: alias is not for identified person"
                player_record = performancerecord.PlayerDBrecord()
                player_record.load_record(primary_record)
                player_record.value.alias = player_record.value.identity

                # None is safe because self.srkey == new_record.srkey.
                # filespec.PLAYER_IDENTITY_FIELD_DEF is correct value otherwise
                # because of how argument is used in edit_record().
                alias_record.edit_record(
                    database, filespec.PLAYER_FILE_DEF, None, player_record
                )
        finally:
            cursor.close()
    except:  # pycodestyle E722: pylint is happy with following 'raise'.
        database.backout()
        raise
    database.commit()


def break_person_into_picked_players(database, person, aliases):
    """Break aliases of person into new player aliases on database.

    The aliases of person become separate new players.

    The changes are applied to database.

    """
    value = performancerecord.PersonDBvalue()
    value.load_alias_index_key(person[0][0])
    selector = database.encode_record_selector(value.alias_index_key())
    database.start_transaction()
    try:
        recordlist = database.recordlist_key(
            filespec.PLAYER_FILE_DEF,
            filespec.PERSON_ALIAS_FIELD_DEF,
            key=selector,
        )
        count = recordlist.count_records()
        if count == 0:
            raise PersonToPlayer("Cannot break: person record does not exist")
        if count > 1:
            raise PersonToPlayer("Cannot break: person record duplicated")
        primary_record = identify_item.get_first_item_on_recordlist(
            database,
            recordlist,
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYER_FIELD_DEF,
        )
        person_record = performancerecord.PlayerDBrecord(
            valueclass=performancerecord.PersonDBvalue
        )
        person_record.load_record(primary_record)
        if person_record.value.identity != person_record.value.alias:
            database.backout()
            return "Cannot break: selection is not the identified person"
        identity = person_record.value.identity
        for alias in aliases:
            value.load_alias_index_key(alias[0])
            selector = database.encode_record_selector(value.alias_index_key())
            recordlist = database.recordlist_key(
                filespec.PLAYER_FILE_DEF,
                filespec.PERSON_ALIAS_FIELD_DEF,
                key=selector,
            )
            count = recordlist.count_records()
            if count > 1:
                raise PlayerToPerson(
                    "Cannot break: person alias record duplicated"
                )
            if count == 0:
                raise PlayerToPerson(
                    "Cannot break: person alias record does not exist"
                )
            primary_record = identify_item.get_first_item_on_recordlist(
                database,
                recordlist,
                filespec.PLAYER_FILE_DEF,
                filespec.PLAYER_FIELD_DEF,
            )
            player_record = performancerecord.PlayerDBrecord()
            player_record.load_record(primary_record)
            if identity != player_record.value.alias:
                database.backout()
                return "".join(
                    (
                        "One of the bookmarked players is not aliased ",
                        "to same player as selection player ",
                        "so no changes done",
                    )
                )
            alias_record = performancerecord.PlayerDBrecord(
                valueclass=performancerecord.PersonDBvalue
            )
            alias_record.load_record(primary_record)
            player_record.value.alias = player_record.value.identity

            # None is safe because self.srkey == new_record.srkey.
            # filespec.PLAYER_ALIAS_FIELD_DEF is correct value otherwise
            # because of how argument is used in edit_record().
            alias_record.edit_record(
                database, filespec.PLAYER_FILE_DEF, None, player_record
            )
    except:  # pycodestyle E722: pylint is happy with following 'raise'.
        database.backout()
        raise
    database.commit()
    return None


def change_identified_person(database, player):
    """Change identified person to player on database.

    All aliases of player have their alias changed to player identity.

    The changes are applied to database.

    """
    value = performancerecord.PersonDBvalue()
    value.load_alias_index_key(player[0][0])
    selector = database.encode_record_selector(value.alias_index_key())
    database.start_transaction()
    try:
        recordlist = database.recordlist_key(
            filespec.PLAYER_FILE_DEF,
            filespec.PERSON_ALIAS_FIELD_DEF,
            key=selector,
        )
        count = recordlist.count_records()
        if count == 0:
            raise PersonIdentity("Cannot change: player record does not exist")
        if count > 1:
            raise PersonIdentity("Cannot change: player record duplicated")
        primary_record = identify_item.get_first_item_on_recordlist(
            database,
            recordlist,
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYER_FIELD_DEF,
        )
        selection_record = performancerecord.PlayerDBrecord(
            valueclass=performancerecord.PersonDBvalue
        )
        selection_record.load_record(primary_record)
        if selection_record.value.identity == selection_record.value.alias:
            database.backout()
            return "Not changed: selection is already the identified person"

        recordlist = database.recordlist_key(
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYER_IDENTITY_FIELD_DEF,
            key=database.encode_record_selector(selection_record.value.alias),
        )
        count = recordlist.count_records()
        if count == 0:
            raise PlayerToPerson(
                "Cannot change: no players with this identity"
            )
        cursor = database.database_cursor(
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYER_FIELD_DEF,
            recordset=recordlist,
        )
        try:
            while True:
                record = cursor.next()
                if not record:
                    break
                alias_record = performancerecord.PlayerDBrecord(
                    valueclass=performancerecord.PersonDBvalue
                )
                alias_record.load_record(
                    database.get_primary_record(
                        filespec.PLAYER_FILE_DEF, record[0]
                    )
                )
                if selection_record.value.alias != alias_record.value.alias:
                    database.backout()
                    return "Cannot change: alias is not for identified person"
                clone_record = alias_record.clone()
                clone_record.value.alias = selection_record.value.identity
                assert alias_record.srkey == clone_record.srkey
                alias_record.edit_record(
                    database, filespec.PLAYER_FILE_DEF, None, clone_record
                )
        finally:
            cursor.close()
    except:  # pycodestyle E722: pylint is happy with following 'raise'.
        database.backout()
        raise
    database.commit()
