# performancerecord.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Record definition classes for Chess Performance Calculation data."""

import os
from ast import literal_eval

from solentware_base.core.record import KeyData
from solentware_base.core.record import ValueList, Record
from solentware_base.core.segmentsize import SegmentSize

from pgn_read.core import tagpair_parser

from . import filespec
from . import constants
from . import identity

# The sets of values reserved for processing status in GAME_STATUS_FIELD_DEF
# index.
_FILE_NAMES_TO_BE_POPULATED = (
    filespec.PLAYER_FILE_DEF,
    filespec.EVENT_FILE_DEF,
    filespec.TIME_FILE_DEF,
    filespec.MODE_FILE_DEF,
)
_FIELD_NAMES_TO_BE_POPULATED = (
    filespec.GAME_PGNFILE_FIELD_DEF,
    filespec.GAME_NUMBER_FIELD_DEF,
    filespec.GAME_DATE_FIELD_DEF,
    filespec.GAME_TIMECONTROL_FIELD_DEF,
    filespec.GAME_MODE_FIELD_DEF,
    filespec.GAME_PLAYER_FIELD_DEF,
    filespec.GAME_EVENT_FIELD_DEF,
    filespec.GAME_STATUS_FIELD_DEF,
)
_NAMES_NOT_ALLOWED_IN_STATUS = set(_FILE_NAMES_TO_BE_POPULATED).union(
    _FIELD_NAMES_TO_BE_POPULATED
)
_FILE_AND_FIELD_NAMES_TO_BE_POPULATED = tuple(_NAMES_NOT_ALLOWED_IN_STATUS)


class GameDBvalueError(Exception):
    """Raise if certain file names are given for index packing."""


class GameDBkey(KeyData):
    """Primary key of game."""


class GameDBvalue(ValueList):
    """Game header data.

    All import stages where data is copied to another file are indexed.

    The PGN file name and game number within file are recorded.

    All the PGN tag name and value pairs are recorded.  The tag names
    of interest for game selection are: Result, Date, Round, TimeControl,
    and Mode.

    Other tag names are relevant for identifying the event and players
    of the white and black pieces.  These are listed in the PlayerDBvalue
    class.
    """

    attributes = dict(
        reference=None,  # dict of PGN file name and game number within file.
        headers=None,  # dict of PGN tag name and value pairs for game.
        # status=None,  # set of import actions not yet done.
    )
    _attribute_order = ("headers", "reference")  # , "status")
    assert set(_attribute_order) == set(attributes)

    def pack(self):
        """Extend, return game record and index data."""
        val = super().pack()
        self.pack_detail(val[1])
        return val

    def verify_status_values(self):
        """Raise GameDBvalueError if certain values supplied for status.

        These values are the names of the Player, Event, Time, and Mode,
        files.

        """
        # if self.status and self.status.intersection(
        #    _NAMES_NOT_ALLOWED_IN_STATUS
        # ):
        #    raise GameDBvalueError(
        #        "One or more file names is in 'status' attribute"
        #    )

    def pack_detail(self, index):
        """Fill index with detail from value.

        Some 'gamestatus' indicies are generated: the ones indicating
        that the 'player', 'event', 'time', and 'mode', files have not
        been populated.  But it is an error if self.status contains
        these references.

        """
        # self.verify_status_values()
        for attr, defn in (
            (constants.FILE, filespec.GAME_PGNFILE_FIELD_DEF),
            (constants.GAME, filespec.GAME_NUMBER_FIELD_DEF),
        ):
            data = self.reference.get(attr)
            if data is not None:
                index[defn] = [data]
            else:
                index[defn] = []
        headers = self.headers
        for attr, defn in (
            (constants.TAG_DATE, filespec.GAME_DATE_FIELD_DEF),
            (constants.TAG_TIMECONTROL, filespec.GAME_TIMECONTROL_FIELD_DEF),
            (constants.TAG_MODE, filespec.GAME_MODE_FIELD_DEF),
        ):
            data = headers.get(attr)
            if data is not None:
                index[defn] = [data]
            else:
                index[defn] = []
        index[filespec.GAME_PLAYER_FIELD_DEF] = [
            self.black_key(),
            self.white_key(),
        ]
        index[filespec.GAME_EVENT_FIELD_DEF] = [
            repr(
                (
                    headers.get(constants.TAG_EVENT),
                    headers.get(constants.TAG_EVENTDATE),
                    headers.get(constants.TAG_SECTION),
                    headers.get(constants.TAG_STAGE),
                )
            ),
        ]
        # index[filespec.GAME_STATUS_FIELD_DEF] = list(
        #    _FILE_NAMES_TO_BE_POPULATED
        # )

    def black_key(self):
        """Return the black key for the gameplayer index."""
        headers = self.headers
        return repr(
            (
                headers.get(constants.TAG_BLACK),
                headers.get(constants.TAG_EVENT),
                headers.get(constants.TAG_EVENTDATE),
                headers.get(constants.TAG_SECTION),
                headers.get(constants.TAG_STAGE),
                headers.get(constants.TAG_BLACKTEAM),
                headers.get(constants.TAG_BLACKFIDEID),
            )
        )

    def white_key(self):
        """Return the white key for the gameplayer index."""
        headers = self.headers
        return repr(
            (
                headers.get(constants.TAG_WHITE),
                headers.get(constants.TAG_EVENT),
                headers.get(constants.TAG_EVENTDATE),
                headers.get(constants.TAG_SECTION),
                headers.get(constants.TAG_STAGE),
                headers.get(constants.TAG_WHITETEAM),
                headers.get(constants.TAG_WHITEFIDEID),
            )
        )

    def __eq__(self, other):
        """Return True if attributes of self and other are same."""
        sdict = self.__dict__
        odict = other.__dict__
        if len(sdict) != len(odict):
            return False
        for item in sdict:
            if item not in odict:
                return False
            if not isinstance(sdict[item], type(odict[item])):
                return False
            if sdict[item] != odict[item]:
                return False
        return True

    def __ge__(self, other):
        """Return True always (consistent with __gt__)."""
        return True

    def __gt__(self, other):
        """Return True if __ne__ is True."""
        return self.__ne__(other)

    def __le__(self, other):
        """Return True always (consistent with __lt__)."""
        return True

    def __lt__(self, other):
        """Return True if __ne__ is True."""
        return self.__ne__(other)

    def __ne__(self, other):
        """Return True if attributes of self and other are different."""
        sdict = self.__dict__
        odict = other.__dict__
        if len(sdict) != len(odict):
            return True
        for item in sdict:
            if item not in odict:
                return True
            if not isinstance(sdict[item], type(odict[item])):
                return True
            if sdict[item] != odict[item]:
                return True
        return False


class GameDBImportvalue(GameDBvalue):
    """Customise GameDBvalue to store stages to be done.

    All import stages are indexed.
    """

    def pack_detail(self, index):
        """Override, fill index with detail from value.

        Game record is indexed by game identifier (PGN file and number
        within file) and import status only.

        """
        # self.verify_status_values()
        index[filespec.GAME_STATUS_FIELD_DEF] = list(
            _FILE_AND_FIELD_NAMES_TO_BE_POPULATED
        )


class GameDBrecord(Record):
    """Game record."""

    def __init__(self, keyclass=GameDBkey, valueclass=GameDBvalue):
        """Customise Record with ResultsDBkeyGame and ResultsDBvalueGame."""
        super().__init__(keyclass, valueclass)

    def get_keys(self, datasource=None, partial=None):
        """Override, return [(key, value)] for datasource or []."""
        try:
            if partial is not None:
                return []
            srkey = datasource.dbhome.encode_record_number(self.key.pack())
            if datasource.primary:
                return [(srkey, self.srvalue)]
            dbname = datasource.dbname
            if dbname == filespec.GAME_DATE_FIELD_DEF:
                return [(self.value.date, srkey)]
            if dbname == filespec.GAME_NUMBER_FIELD_DEF:
                return [(repr((self.value.file, self.value.number)), srkey)]
            if dbname == filespec.GAME_TIMECONTROL_FIELD_DEF:
                return [(self.value.timecontrol, srkey)]
            if dbname == filespec.GAME_MODE_FIELD_DEF:
                return [(self.value.mode, srkey)]
            return []
        except:  # pycodestyle E722: pylint is happy with following 'raise'.
            if datasource is None:
                return []
            raise


class GameDBImporter(GameDBrecord):
    """Extend with methods to import multiple game headers from PGN files."""

    def import_pgn_headers(
        self,
        database,
        path,
        reporter=None,
        quit_event=None,
    ):
        """Return True if import to database of PGN files in path succeeds.

        Games without a tag pair for tag name "Result", or with this tag
        pair but a tag value other than '1-0', '0-1', or '1/2-1/2', are
        ignored.

        Do nothing and return False if path argument is not a directory or
        does not exist.

        *.pgn files are read trying utf-8 first and then iso-8859-1 with
        the latter expected to succeed always possibly not accurately
        representing the *.pgn file content.

        quit_event allows the import to be interrupted by passing an Event
        instance which get queried after processing each game.

        """
        if not os.path.exists(path):
            if reporter is not None:
                reporter.append_text_only("")
                reporter.append_text(path + " does not exist")
            return False
        if not os.path.isdir(path):
            if reporter is not None:
                reporter.append_text_only("")
                reporter.append_text(path + " is not a directory")
            return False
        self.value.headers = {}
        self.value.reference = {}
        done_ok = self._extract_pgn_headers_from_directory(
            database, path, reporter, quit_event
        )
        if reporter is not None:
            reporter.append_text_only("")
        return done_ok

    def count_pgn_games(
        self,
        database,
        path,
        reporter=None,
        quit_event=None,
    ):
        """Return number of games in files or False.

        Games without a tag pair for tag name "Result", or with this tag
        pair but a tag value other than '1-0', '0-1', or '1/2-1/2', are
        ignored.

        Do nothing and return False if path argument is not a directory or
        does not exist.

        *.pgn files are read trying utf-8 first and then iso-8859-1 with
        the latter expected to succeed always possibly not accurately
        representing the *.pgn file content.

        quit_event allows the import to be interrupted by passing an Event
        instance which get queried after processing each game.

        """
        if not os.path.exists(path):
            if reporter is not None:
                reporter.append_text_only("")
                reporter.append_text(path + " does not exist")
            return False
        if not os.path.isdir(path):
            if reporter is not None:
                reporter.append_text_only("")
                reporter.append_text(path + " is not a directory")
            return False
        done_ok = self._count_pgn_games_in_directory(
            database, path, reporter, quit_event
        )
        if reporter is not None:
            reporter.append_text_only("")
        return done_ok

    def _process_pgn_headers_from_directory(
        self, database, pgnpath, reporter, quit_event
    ):
        """Extract PGN headers from directories and *.pgn files in pgnpath."""
        if reporter is not None:
            reporter.append_text_only("")
            reporter.append_text("Processing files in " + pgnpath)
        for entry in os.listdir(pgnpath):
            path = os.path.join(pgnpath, entry)
            if os.path.isfile(path):
                if not self._extract_pgn_headers_from_file(
                    database, path, reporter, quit_event
                ):
                    return False
        for entry in os.listdir(pgnpath):
            path = os.path.join(pgnpath, entry)
            if os.path.isdir(path):
                if not self._extract_pgn_headers_from_directory(
                    database, path, reporter, quit_event
                ):
                    return False
        return True

    def _process_pgn_games_from_directory(
        self, database, pgnpath, reporter, quit_event
    ):
        """Count games in directories and *.pgn files in pgnpath."""
        if reporter is not None:
            reporter.append_text_only("")
            reporter.append_text("Processing files in " + pgnpath)
        directory_count = 0
        for entry in os.listdir(pgnpath):
            path = os.path.join(pgnpath, entry)
            if os.path.isfile(path):
                count = self._count_pgn_games_in_file(
                    database, path, reporter, quit_event
                )
                if count is None:
                    return False
                directory_count += count
        for entry in os.listdir(pgnpath):
            path = os.path.join(pgnpath, entry)
            if os.path.isdir(path):
                count = self._count_pgn_games_in_directory(
                    database, path, reporter, quit_event
                )
                if count is None:
                    return False
                directory_count += count
        return directory_count

    def _extract_pgn_headers_from_directory(
        self, database, pgnpath, reporter, quit_event
    ):
        """Search directory pgnpath for *.pgn files and extract headers."""
        return self._process_pgn_headers_from_directory(
            database,
            pgnpath,
            reporter,
            quit_event,
        )

    # Probably needed only by DPT database engine.
    # Probably only in this class to use _process_pgn_headers_from_directory
    # machinery and from similarity to copy_* classes.
    def _count_pgn_games_in_directory(
        self, database, pgnpath, reporter, quit_event
    ):
        """Search directory tree pgnpath for *.pgn files and count games."""
        return self._process_pgn_games_from_directory(
            database,
            pgnpath,
            reporter,
            quit_event,
        )

    @staticmethod
    def _is_file_pgn_ext(pgnpath, reporter):
        """Return True if pgnpath is a PGN file."""
        if not os.path.isfile(pgnpath):
            if reporter is not None:
                reporter.append_text_only("")
                reporter.append_text(pgnpath + " is not a file")
                reporter.append_text_only("")
            return False
        if not os.path.splitext(pgnpath)[1].lower() == constants.PGNEXT:
            if reporter is not None:
                reporter.append_text_only("")
                reporter.append_text(
                    pgnpath + " is not a " + constants.PGNEXT + " file"
                )
                reporter.append_text_only("")
            return False
        return True

    def _extract_pgn_headers_from_file(
        self, database, pgnpath, reporter, quit_event
    ):
        """Return True if import succeeds or pgnpath is not a PGN file."""
        del quit_event
        if not self._is_file_pgn_ext(pgnpath, reporter):
            return True
        if reporter is not None:
            reporter.append_text_only("")
            reporter.append_text(
                "Extracting game headers from " + os.path.basename(pgnpath)
            )

        # Maybe /home is symlink to /usr/home like on FreeBSD.
        user = os.path.realpath(os.path.expanduser("~"))

        if pgnpath.startswith(user):
            refbase = pgnpath[len(user) + 1 :]  # black says '1 :'.
        else:
            refbase = pgnpath
        parser = tagpair_parser.PGNTagPair(
            game_class=tagpair_parser.TagPairGame
        )
        self.set_database(database)
        reference = self.value.reference
        db_segment_size = SegmentSize.db_segment_size
        reference[constants.FILE] = os.path.basename(refbase)
        game_number = 0
        copy_number = 0
        seen_number = 0
        game_offset = None
        # The PGN specification assumes iso-8859-1 encoding but try
        # utf-8 encoding first.
        encoding = None
        for try_encoding in ("utf-8", "iso-8859-1"):
            with open(pgnpath, mode="r", encoding=try_encoding) as pgntext:
                try:
                    while True:
                        if not pgntext.read(1024 * 1000):
                            encoding = try_encoding
                            break
                except UnicodeDecodeError:
                    pass
        if encoding is None:
            if reporter is not None:
                reporter.append_text_only("")
                reporter.append_text(
                    "".join(
                        (
                            "Unable to read ",
                            reference[constants.FILE],
                            " as utf-8 or iso-8859-1 ",
                            "encoding.",
                        )
                    )
                )
            return True
        file_games = database.recordlist_key(
            filespec.GAME_FILE_DEF,
            filespec.GAME_PGNFILE_FIELD_DEF,
            key=database.encode_record_selector(reference[constants.FILE]),
        )
        file_count = file_games.count_records()
        file_games.close()
        if file_count:
            if reporter is not None:
                reporter.append_text_only("")
                reporter.append_text(
                    "".join(
                        (
                            str(file_count),
                            " games from file ",
                            reference[constants.FILE],
                            " already on database: only missing ",
                            "game numbers will be copied.",
                        )
                    )
                )
        with open(pgnpath, mode="r", encoding=encoding) as pgntext:
            for collected_game in parser.read_games(pgntext):
                game_offset = collected_game.game_offset
                game_number += 1
                reference[constants.GAME] = str(game_number)
                if file_count:
                    number_games = database.recordlist_key(
                        filespec.GAME_FILE_DEF,
                        filespec.GAME_NUMBER_FIELD_DEF,
                        key=database.encode_record_selector(
                            reference[constants.GAME]
                        ),
                    )
                    number_count = number_games.count_records()
                    if number_count:
                        file_games = database.recordlist_key(
                            filespec.GAME_FILE_DEF,
                            filespec.GAME_PGNFILE_FIELD_DEF,
                            key=database.encode_record_selector(
                                reference[constants.FILE]
                            ),
                        )
                        present_game = number_games & file_games
                        present_count = present_game.count_records()
                        present_game.close()
                        if present_count:
                            file_games.close()
                            number_games.close()
                            continue
                        file_games.close()
                    number_games.close()
                seen_number += 1
                self.value.headers = collected_game.pgn_tags
                headers = self.value.headers
                if (
                    headers.get(constants.TAG_RESULT)
                    in constants.WIN_DRAW_LOSS
                ):
                    copy_number += 1
                    self.key.recno = None
                    self.put_record(self.database, filespec.GAME_FILE_DEF)
                    if copy_number % db_segment_size == 0:
                        database.commit()
                        database.start_transaction()
                        if reporter is not None:
                            reporter.append_text(
                                "".join(
                                    (
                                        "Record ",
                                        str(self.key.recno),
                                        " is from game ",
                                        reference[constants.GAME],
                                        " in ",
                                        reference[constants.FILE],
                                    )
                                )
                            )
                elif reporter is not None:
                    if headers.get(constants.TAG_RESULT) is None:
                        reporter.append_text_only(
                            "".join(
                                (
                                    "No result tag in game ",
                                    reference[constants.GAME],
                                    " in ",
                                    reference[constants.FILE],
                                )
                            )
                        )
                    else:
                        reporter.append_text_only(
                            "".join(
                                (
                                    headers.get(constants.TAG_RESULT),
                                    " is result of game ",
                                    reference[constants.GAME],
                                    " in ",
                                    reference[constants.FILE],
                                )
                            )
                        )
        if reporter is not None and game_offset is not None:
            reporter.append_text_only("")
            reporter.append_text(
                "".join(
                    (
                        str(game_number),
                        " games read from ",
                        reference[constants.FILE],
                        " to character ",
                        str(game_offset),
                    )
                )
            )
            reporter.append_text_only(
                "".join(
                    (
                        str(copy_number),
                        " games added to database.",
                    )
                )
            )
            reporter.append_text_only(
                "".join(
                    (
                        str(file_count),
                        " games already on database.",
                    )
                )
            )
            reporter.append_text_only(
                "".join(
                    (
                        str(seen_number - copy_number),
                        " games had errors and were not copied.",
                    )
                )
            )
        return True

    # Probably needed only by DPT database engine.
    # Probably only in this class to use _process_pgn_headers_from_directory
    # machinery and from similarity to copy_* classes.
    def _count_pgn_games_in_file(
        self, database, pgnpath, reporter, quit_event
    ):
        """Return True if import succeeds or pgnpath is not a PGN file."""
        del database, quit_event
        if not self._is_file_pgn_ext(pgnpath, reporter):
            return True
        if reporter is not None:
            reporter.append_text_only("")
            reporter.append_text(
                "Counting games in " + os.path.basename(pgnpath)
            )

        # Maybe /home is symlink to /usr/home like on FreeBSD.
        user = os.path.realpath(os.path.expanduser("~"))

        if pgnpath.startswith(user):
            refbase = pgnpath[len(user) + 1 :]  # black says '1 :'.
        else:
            refbase = pgnpath
        parser = tagpair_parser.PGNTagPair(game_class=tagpair_parser.GameCount)
        game_number = 0
        game_offset = None
        # The PGN specification assumes 'iso-8859-1' encoding but do not
        # bother trying 'utf-8' encoding first because things are only
        # being counted.
        with open(pgnpath, mode="r", encoding="iso-8859-1") as pgntext:
            for collected_game in parser.read_games(pgntext):
                game_offset = collected_game.game_offset
                game_number += 1
        if reporter is not None and game_offset is not None:
            reporter.append_text_only("")
            reporter.append_text(
                "".join(
                    (
                        str(game_number),
                        " games read from ",
                        os.path.basename(refbase),
                        " to character ",
                        str(game_offset),
                    )
                )
            )
        return game_number


class PlayerDBkey(KeyData):
    """Primary key of player."""


class _PlayerDBvalue(ValueList):
    """Player data.

    This class is not intended for direct use as it lacks an extended
    version of the pack() method.  Subclasses will need to supply a
    suitable pack() method.
    """

    attributes = dict(
        name=None,  # TAG_BLACK or TAG_WHITE.
        event=None,  # TAG_EVENT.
        eventdate=None,  # TAG_EVENTDATE.
        section=None,  # TAG_SECTION.
        stage=None,  # TAG_STAGE.
        team=None,  # TAG_BLACKTEAM or TAG_WHITETEAM.
        fideid=None,  # TAG_BLACKFIDEID or TAG_WHITEFIDEID.
        alias=None,
        identity=None,
    )
    _attribute_order = (
        "name",
        "event",
        "eventdate",
        "section",
        "stage",
        "team",
        "fideid",
        "alias",
        "identity",
    )
    assert set(_attribute_order) == set(attributes)

    def __init__(self):
        """Customise ValueList for player data."""
        super().__init__()
        self.name = None
        self.event = None
        self.eventdate = None
        self.section = None
        self.stage = None
        self.team = None
        self.fideid = None
        self.alias = None
        self.identity = None

    def empty(self):
        """(Re)Initialize value attribute."""
        self.name = None
        self.event = None
        self.eventdate = None
        self.section = None
        self.stage = None
        self.team = None
        self.fideid = None
        self.alias = None
        self.identity = None

    def alias_index_key(self):
        """Return the key for the playeralias or persionalias index."""
        return repr(
            (
                self.name,
                self.event,
                self.eventdate,
                self.section,
                self.stage,
                self.team,
                self.fideid,
            )
        )

    def load_alias_index_key(self, value):
        """Bind playeralias or personalias index attributes to value items."""
        (
            self.name,
            self.event,
            self.eventdate,
            self.section,
            self.stage,
            self.team,
            self.fideid,
        ) = literal_eval(value)


class PlayerDBvalue(_PlayerDBvalue):
    """Player data for record not yet identified with a person.

    When used to update database the pack() method causes the personalias
    index to be cleared of references to the record and the playeralias
    index to be populated with a reference.

    Expected use is PlayerDBrecord(valueclass=PlayerDBvalue).
    """

    def pack(self):
        """Delegate to generate player data then add index data.

        Set playeralias index value to [key] and personalias index to [].

        """
        val = super().pack()
        index = val[1]
        index[filespec.PLAYER_ALIAS_FIELD_DEF] = [self.alias_index_key()]
        index[filespec.PLAYER_UNIQUE_FIELD_DEF] = []
        index[filespec.PLAYER_IDENTITY_FIELD_DEF] = []
        index[filespec.PERSON_ALIAS_FIELD_DEF] = []
        return val


class PersonDBvalue(_PlayerDBvalue):
    """Player data for record identified with a person.

    When used to update database the pack() method causes the playeralias
    index to be cleared of references to the record and the personalias
    index to be populated with a reference.

    Expected use is PlayerDBrecord(valueclass=PersonDBvalue).
    """

    def pack(self):
        """Delegate to generate player data then add index data.

        Set personalias index value to [key] and playeralias index to [].

        """
        val = super().pack()
        index = val[1]
        index[filespec.PLAYER_ALIAS_FIELD_DEF] = []
        if self.identity != self.alias:
            index[filespec.PLAYER_UNIQUE_FIELD_DEF] = []
        else:
            index[filespec.PLAYER_UNIQUE_FIELD_DEF] = [self.alias]
        index[filespec.PLAYER_IDENTITY_FIELD_DEF] = [self.alias]
        index[filespec.PERSON_ALIAS_FIELD_DEF] = [self.alias_index_key()]
        return val


class PlayerDBrecord(Record):
    """Customise Record with PlayerDBkey and PlayerDBvalue by default."""

    def __init__(self, keyclass=PlayerDBkey, valueclass=PlayerDBvalue):
        """Delegate with keyclass and valueclass arguments."""
        super().__init__(keyclass, valueclass)

    def get_keys(self, datasource=None, partial=None):
        """Override, return [(key, value)] for datasource or []."""
        try:
            if partial is not None:
                return []
            srkey = datasource.dbhome.encode_record_number(self.key.pack())
            if datasource.primary:
                return [(srkey, self.srvalue)]
            dbname = datasource.dbname
            if dbname == filespec.PLAYER_ALIAS_FIELD_DEF:
                return [(self.value.alias_index_key(), srkey)]
            if dbname == filespec.PLAYER_IDENTITY_FIELD_DEF:
                return [(self.value.alias, srkey)]
            if dbname == filespec.PERSON_ALIAS_FIELD_DEF:
                return [(self.value.alias_index_key(), srkey)]
            return []
        except:  # pycodestyle E722: pylint is happy with following 'raise'.
            if datasource is None:
                return []
            raise


class PlayerDBImporter(PlayerDBrecord):
    """Extend with methods to import multiple game headers from PGN files."""

    def copy_player_names_from_games(
        self,
        database,
        reporter=None,
        quit_event=None,
        **kwargs,
    ):
        """Return True if copy player names from games file succeeds.

        quit_event allows the import to be interrupted by passing an Event
        instance which get queried after processing each game.
        kwargs soaks up arguments not used in this method.

        """
        del kwargs
        if reporter is not None:
            reporter.append_text("Copy player names from games.")
        cursor = database.database_cursor(
            filespec.GAME_FILE_DEF, filespec.GAME_PLAYER_FIELD_DEF
        )
        value = self.value
        db_segment_size = SegmentSize.db_segment_size
        game_count = 0
        onfile_count = 0
        copy_count = 0
        prev_record = None
        while True:
            record = cursor.next()
            if record is None:
                break
            this_record = literal_eval(record[0])
            if prev_record == this_record:
                continue
            game_count += 1
            prev_record = this_record
            (
                value.name,
                value.event,
                value.eventdate,
                value.section,
                value.stage,
                value.team,
                value.fideid,
            ) = this_record
            alias = value.alias_index_key()
            if quit_event and quit_event.is_set():
                if reporter is not None:
                    reporter.append_text_only("")
                    reporter.append_text("Copy stopped.")
                return False
            if database.recordlist_key(
                filespec.PLAYER_FILE_DEF,
                filespec.PERSON_ALIAS_FIELD_DEF,
                key=database.encode_record_selector(alias),
            ).count_records():
                onfile_count += 1
                continue
            if database.recordlist_key(
                filespec.PLAYER_FILE_DEF,
                filespec.PLAYER_ALIAS_FIELD_DEF,
                key=database.encode_record_selector(alias),
            ).count_records():
                onfile_count += 1
                continue
            copy_count += 1
            pid = identity.get_next_player_identity_value_after_allocation(
                database
            )
            value.alias = pid
            value.identity = pid
            self.key.recno = None
            self.put_record(database, filespec.PLAYER_FILE_DEF)
            if int(pid) % db_segment_size == 0:
                # Need the cursor wrapping in berkeleydb, bsddb3, db_tkinter
                # and lmdb too.
                cursor.close()
                database.commit()
                database.start_transaction()
                cursor = database.database_cursor(
                    filespec.GAME_FILE_DEF, filespec.GAME_PLAYER_FIELD_DEF
                )
                cursor.setat(record)

                if reporter is not None:
                    reporter.append_text(
                        "".join(
                            (
                                "Player ",
                                value.name,
                                " is record ",
                                str(self.key.recno),
                            )
                        )
                    )
        if reporter is not None:
            reporter.append_text_only("")
            reporter.append_text(
                "".join(
                    (
                        str(copy_count),
                        " players added to database.",
                    )
                )
            )
            reporter.append_text_only(
                "".join(
                    (
                        str(onfile_count),
                        " players already on database.",
                    )
                )
            )
            reporter.append_text_only(
                "".join(
                    (
                        str(game_count),
                        " game references processed.",
                    )
                )
            )
            reporter.append_text_only("")
        return True

    def count_player_names_to_be_copied_from_games(
        self,
        database,
        reporter=None,
        quit_event=None,
        **kwargs,
    ):
        """Return number of player names in games file but not players file.

        quit_event allows the import to be interrupted by passing an Event
        instance which get queried after processing each game.
        kwargs soaks up arguments not used in this method.

        """
        del kwargs
        if reporter is not None:
            reporter.append_text("Count player names to be copied from games.")
        cursor = database.database_cursor(
            filespec.GAME_FILE_DEF, filespec.GAME_PLAYER_FIELD_DEF
        )
        value = self.value
        prev_record = None
        count = 0
        while True:
            record = cursor.next()
            if record is None:
                break
            this_record = literal_eval(record[0])
            if prev_record == this_record:
                continue
            prev_record = this_record
            (
                value.name,
                value.event,
                value.eventdate,
                value.section,
                value.stage,
                value.team,
                value.fideid,
            ) = this_record
            alias = value.alias_index_key()
            if quit_event and quit_event.is_set():
                if reporter is not None:
                    reporter.append_text_only("")
                    reporter.append_text("Count stopped.")
                return None
            if database.recordlist_key(
                filespec.PLAYER_FILE_DEF,
                filespec.PERSON_ALIAS_FIELD_DEF,
                key=database.encode_record_selector(alias),
            ).count_records():
                continue
            if database.recordlist_key(
                filespec.PLAYER_FILE_DEF,
                filespec.PLAYER_ALIAS_FIELD_DEF,
                key=database.encode_record_selector(alias),
            ).count_records():
                continue
            count += 1
        if reporter is not None:
            reporter.append_text(
                str(count) + " player names to be copied from games."
            )
        return count


class SelectorDBkey(KeyData):
    """Primary key of game selector."""


class SelectorDBvalue(ValueList):
    """Game Selector data."""

    attributes = dict(
        name=None,
        from_date=None,
        to_date=None,
        person_identity=None,
        event_identities=None,
        time_control_identity=None,
        mode_identity=None,
    )
    _attribute_order = (
        "person_identity",
        "name",
        "from_date",
        "to_date",
        "event_identities",
        "time_control_identity",
        "mode_identity",
    )
    assert set(_attribute_order) == set(attributes)

    def __init__(self):
        """Customise ValueList for identity data."""
        super().__init__()
        self.name = None
        self.from_date = None
        self.to_date = None
        self.person_identity = None
        self.time_control_identity = None
        self.mode_identity = None
        self.event_identities = []

    def empty(self):
        """(Re)Initialize value attribute."""
        self.name = None
        self.from_date = None
        self.to_date = None
        self.person_identity = None
        self.time_control_identity = None
        self.mode_identity = None
        self.event_identities = []

    def pack(self):
        """Generate game selector record and index data."""
        val = super().pack()
        index = val[1]
        index[filespec.RULE_FIELD_DEF] = [self.name]
        return val


class SelectorDBrecord(Record):
    """Customise Record with SelectorDBkey and SelectorDBvalue by default."""

    def __init__(self, keyclass=SelectorDBkey, valueclass=SelectorDBvalue):
        """Delegate with keyclass and valueclass arguments."""
        super().__init__(keyclass, valueclass)

    def get_keys(self, datasource=None, partial=None):
        """Override, return [(key, value)] for datasource or []."""
        try:
            if partial is not None:
                return []
            srkey = datasource.dbhome.encode_record_number(self.key.pack())
            if datasource.primary:
                return [(srkey, self.srvalue)]
            dbname = datasource.dbname
            if dbname == filespec.RULE_FIELD_DEF:
                return [(self.value.name, srkey)]
            return []
        except:  # pycodestyle E722: pylint is happy with following 'raise'.
            if datasource is None:
                return []
            raise


class EventDBkey(KeyData):
    """Primary key of event."""


class EventDBvalue(ValueList):
    """Event data."""

    attributes = dict(
        event=None,  # TAG_EVENT.
        eventdate=None,  # TAG_EVENTDATE.
        section=None,  # TAG_SECTION.
        stage=None,  # TAG_STAGE.
        alias=None,
        identity=None,
    )
    _attribute_order = (
        "event",
        "eventdate",
        "section",
        "stage",
        "alias",
        "identity",
    )
    assert set(_attribute_order) == set(attributes)

    def __init__(self):
        """Customise ValueList for player data."""
        super().__init__()
        self.event = None
        self.eventdate = None
        self.section = None
        self.stage = None
        self.alias = None
        self.identity = None

    def empty(self):
        """(Re)Initialize value attribute."""
        self.event = None
        self.eventdate = None
        self.section = None
        self.stage = None
        self.alias = None
        self.identity = None

    def alias_index_key(self):
        """Return the key for the eventalias index."""
        return repr(
            (
                self.event,
                self.eventdate,
                self.section,
                self.stage,
            )
        )

    def load_alias_index_key(self, value):
        """Bind attributes for the eventalias index to items in value."""
        (
            self.event,
            self.eventdate,
            self.section,
            self.stage,
        ) = literal_eval(value)

    def pack(self):
        """Delegate to generate player data then add index data.

        The eventalias index will have the event name and other descriptive
        detail as it's value, from the alias_index_key() method.

        The eventidentity index will have either the identity number given
        when the record was created (identity attribute), or the identity
        number of the event record which this record currently aliases
        (alias attribute).

        """
        val = super().pack()
        index = val[1]
        index[filespec.EVENT_ALIAS_FIELD_DEF] = [self.alias_index_key()]
        index[filespec.EVENT_IDENTITY_FIELD_DEF] = [self.alias]
        return val


class EventDBrecord(Record):
    """Customise Record with EventDBkey and EventDBvalue by default."""

    def __init__(self, keyclass=EventDBkey, valueclass=EventDBvalue):
        """Delegate with keyclass and valueclass arguments."""
        super().__init__(keyclass, valueclass)

    def get_keys(self, datasource=None, partial=None):
        """Override, return [(key, value)] for datasource or []."""
        try:
            if partial is not None:
                return []
            srkey = datasource.dbhome.encode_record_number(self.key.pack())
            if datasource.primary:
                return [(srkey, self.srvalue)]
            dbname = datasource.dbname
            if dbname == filespec.EVENT_ALIAS_FIELD_DEF:
                return [(self.value.alias_index_key(), srkey)]
            if dbname == filespec.EVENT_IDENTITY_FIELD_DEF:
                return [(self.value.alias, srkey)]
            return []
        except:  # pycodestyle E722: pylint is happy with following 'raise'.
            if datasource is None:
                return []
            raise


class EventDBImporter(EventDBrecord):
    """Extend with methods to import multiple game headers from PGN files."""

    def copy_event_names_from_games(
        self,
        database,
        reporter=None,
        quit_event=None,
        **kwargs,
    ):
        """Return True if copy event names from games file succeeds.

        quit_event allows the import to be interrupted by passing an Event
        instance which get queried after processing each game.
        kwargs soaks up arguments not used in this method.

        """
        del kwargs
        if reporter is not None:
            reporter.append_text("Copy event names from games.")
        cursor = database.database_cursor(
            filespec.GAME_FILE_DEF, filespec.GAME_EVENT_FIELD_DEF
        )
        value = self.value
        db_segment_size = SegmentSize.db_segment_size
        game_count = 0
        onfile_count = 0
        copy_count = 0
        prev_record = None
        while True:
            record = cursor.next()
            if record is None:
                break
            this_record = literal_eval(record[0])
            if prev_record == this_record:
                continue
            game_count += 1
            prev_record = this_record
            (
                value.event,
                value.eventdate,
                value.section,
                value.stage,
            ) = this_record
            alias = value.alias_index_key()
            if quit_event and quit_event.is_set():
                if reporter is not None:
                    reporter.append_text_only("")
                    reporter.append_text("Copy stopped.")
                return False
            if database.recordlist_key(
                filespec.EVENT_FILE_DEF,
                filespec.EVENT_ALIAS_FIELD_DEF,
                key=database.encode_record_selector(alias),
            ).count_records():
                onfile_count += 1
                continue
            copy_count += 1
            pid = identity.get_next_event_identity_value_after_allocation(
                database
            )
            value.alias = pid
            value.identity = pid
            self.key.recno = None
            self.put_record(database, filespec.EVENT_FILE_DEF)
            if int(pid) % db_segment_size == 0:
                # Need the cursor wrapping in berkeleydb, bsddb3, db_tkinter
                # and lmdb too.
                cursor.close()
                database.commit()
                database.start_transaction()
                cursor = database.database_cursor(
                    filespec.GAME_FILE_DEF, filespec.GAME_EVENT_FIELD_DEF
                )
                cursor.setat(record)

                if reporter is not None:
                    reporter.append_text(
                        "".join(
                            (
                                "Event ",
                                value.event,
                                " is record ",
                                str(self.key.recno),
                            )
                        )
                    )
        if reporter is not None:
            reporter.append_text_only("")
            reporter.append_text(
                "".join(
                    (
                        str(copy_count),
                        " events added to database.",
                    )
                )
            )
            reporter.append_text_only(
                "".join(
                    (
                        str(onfile_count),
                        " events already on database.",
                    )
                )
            )
            reporter.append_text_only(
                "".join(
                    (
                        str(game_count),
                        " game references processed.",
                    )
                )
            )
            reporter.append_text_only("")
        return True

    def count_event_names_to_be_copied_from_games(
        self,
        database,
        reporter=None,
        quit_event=None,
        **kwargs,
    ):
        """Return number of event names in games file but not events file.

        quit_event allows the import to be interrupted by passing an Event
        instance which get queried after processing each game.
        kwargs soaks up arguments not used in this method.

        """
        del kwargs
        if reporter is not None:
            reporter.append_text("Count event names to be copied from games.")
        cursor = database.database_cursor(
            filespec.GAME_FILE_DEF, filespec.GAME_EVENT_FIELD_DEF
        )
        value = self.value
        prev_record = None
        count = 0
        while True:
            record = cursor.next()
            if record is None:
                break
            this_record = literal_eval(record[0])
            if prev_record == this_record:
                continue
            prev_record = this_record
            (
                value.event,
                value.eventdate,
                value.section,
                value.stage,
            ) = this_record
            alias = value.alias_index_key()
            if quit_event and quit_event.is_set():
                if reporter is not None:
                    reporter.append_text_only("")
                    reporter.append_text("Count stopped.")
                return None
            if database.recordlist_key(
                filespec.EVENT_FILE_DEF,
                filespec.EVENT_ALIAS_FIELD_DEF,
                key=database.encode_record_selector(alias),
            ).count_records():
                continue
            count += 1
        if reporter is not None:
            reporter.append_text(
                str(count) + " event names to be copied from games."
            )
        return count


class TimeControlDBkey(KeyData):
    """Primary key of time control."""


class TimeControlDBvalue(ValueList):
    """Time control data."""

    attributes = dict(
        timecontrol=None,  # TAG_TIMECONTROL.
        alias=None,
        identity=None,
    )
    _attribute_order = (
        "timecontrol",
        "alias",
        "identity",
    )
    assert set(_attribute_order) == set(attributes)

    def __init__(self):
        """Customise ValueList for time control data."""
        super().__init__()
        self.timecontrol = None
        self.alias = None
        self.identity = None

    def empty(self):
        """(Re)Initialize value attribute."""
        self.timecontrol = None
        self.alias = None
        self.identity = None

    def alias_index_key(self):
        """Return the key for the timealias index."""
        return repr(self.timecontrol)

    def load_alias_index_key(self, value):
        """Bind attributes for the timealias index to items in value."""
        (self.timecontrol,) = literal_eval(value)

    def pack(self):
        """Delegate to generate time control data then add index data.

        The timealias index will have the time control name and other
        descriptive detail as it's value, from the alias_index_key() method.

        The timeidentity index will have either the identity number given
        when the record was created (identity attribute), or the identity
        number of the time control record which this record currently aliases
        (alias attribute).

        """
        val = super().pack()
        index = val[1]
        index[filespec.TIME_ALIAS_FIELD_DEF] = [self.alias_index_key()]
        index[filespec.TIME_IDENTITY_FIELD_DEF] = [self.alias]
        return val


class TimeControlDBrecord(Record):
    """Customise Record with TimeControlDBkey and TimeControlDBvalue."""

    def __init__(
        self, keyclass=TimeControlDBkey, valueclass=TimeControlDBvalue
    ):
        """Delegate with keyclass and valueclass arguments."""
        super().__init__(keyclass, valueclass)

    def get_keys(self, datasource=None, partial=None):
        """Override, return [(key, value)] for datasource or []."""
        try:
            if partial is not None:
                return []
            srkey = datasource.dbhome.encode_record_number(self.key.pack())
            if datasource.primary:
                return [(srkey, self.srvalue)]
            dbname = datasource.dbname
            if dbname == filespec.TIME_ALIAS_FIELD_DEF:
                return [(self.value.alias_index_key(), srkey)]
            if dbname == filespec.TIME_IDENTITY_FIELD_DEF:
                return [(self.value.alias, srkey)]
            return []
        except:  # pycodestyle E722: pylint is happy with following 'raise'.
            if datasource is None:
                return []
            raise


class TimeControlDBImporter(TimeControlDBrecord):
    """Extend with methods to import multiple game headers from PGN files."""

    def copy_time_control_names_from_games(
        self,
        database,
        reporter=None,
        quit_event=None,
        **kwargs,
    ):
        """Return True if copy time control names from games file succeeds.

        quit_event allows the import to be interrupted by passing an Event
        instance which get queried after processing each game.
        kwargs soaks up arguments not used in this method.

        """
        del kwargs
        if reporter is not None:
            reporter.append_text("Copy time control names from games.")
        cursor = database.database_cursor(
            filespec.GAME_FILE_DEF, filespec.GAME_TIMECONTROL_FIELD_DEF
        )
        value = self.value
        db_segment_size = SegmentSize.db_segment_size
        game_count = 0
        onfile_count = 0
        copy_count = 0
        prev_record = None
        while True:
            record = cursor.next()
            if record is None:
                break
            this_record = literal_eval(record[0])
            if prev_record == this_record:
                continue
            game_count += 1
            prev_record = this_record
            value.timecontrol = this_record
            alias = value.alias_index_key()
            if quit_event and quit_event.is_set():
                if reporter is not None:
                    reporter.append_text_only("")
                    reporter.append_text("Copy stopped.")
                return False
            if database.recordlist_key(
                filespec.TIME_FILE_DEF,
                filespec.TIME_ALIAS_FIELD_DEF,
                key=database.encode_record_selector(alias),
            ).count_records():
                onfile_count += 1
                continue
            copy_count += 1
            pid = identity.get_next_timelimit_identity_value_after_allocation(
                database
            )
            value.alias = pid
            value.identity = pid
            self.key.recno = None
            self.put_record(database, filespec.TIME_FILE_DEF)
            if int(pid) % db_segment_size == 0:
                # Need the cursor wrapping in berkeleydb, bsddb3, db_tkinter
                # and lmdb too.
                cursor.close()
                database.commit()
                database.start_transaction()
                cursor = database.database_cursor(
                    filespec.GAME_FILE_DEF, filespec.GAME_TIMECONTROL_FIELD_DEF
                )
                cursor.setat(record)

                if reporter is not None:
                    reporter.append_text(
                        "".join(
                            (
                                "Time control ",
                                value.timecontrol,
                                " is record ",
                                str(self.key.recno),
                            )
                        )
                    )
        if reporter is not None:
            reporter.append_text_only("")
            reporter.append_text(
                "".join(
                    (
                        str(copy_count),
                        " time controls added to database.",
                    )
                )
            )
            reporter.append_text_only(
                "".join(
                    (
                        str(onfile_count),
                        " time controls already on database.",
                    )
                )
            )
            reporter.append_text_only(
                "".join(
                    (
                        str(game_count),
                        " game references processed.",
                    )
                )
            )
            reporter.append_text_only("")
        return True

    def count_time_control_names_to_be_copied_from_games(
        self,
        database,
        reporter=None,
        quit_event=None,
        **kwargs,
    ):
        """Return number of time control names not in time control file.

        quit_event allows the import to be interrupted by passing an Event
        instance which get queried after processing each game.
        kwargs soaks up arguments not used in this method.

        """
        del kwargs
        if reporter is not None:
            reporter.append_text(
                "Count time control names to be copied from games."
            )
        cursor = database.database_cursor(
            filespec.GAME_FILE_DEF, filespec.GAME_TIMECONTROL_FIELD_DEF
        )
        value = self.value
        prev_record = None
        count = 0
        while True:
            record = cursor.next()
            if record is None:
                break
            this_record = literal_eval(record[0])
            if prev_record == this_record:
                continue
            prev_record = this_record
            value.timecontrol = this_record
            alias = value.alias_index_key()
            if quit_event and quit_event.is_set():
                if reporter is not None:
                    reporter.append_text_only("")
                    reporter.append_text("Count stopped.")
                return None
            if database.recordlist_key(
                filespec.TIME_FILE_DEF,
                filespec.TIME_ALIAS_FIELD_DEF,
                key=database.encode_record_selector(alias),
            ).count_records():
                continue
            count += 1
        if reporter is not None:
            reporter.append_text(
                str(count) + " time control names to be copied from games."
            )
        return count


class ModeDBkey(KeyData):
    """Primary key of playing mode."""


class ModeDBvalue(ValueList):
    """Playing mode data."""

    attributes = dict(
        mode=None,  # TAG_MODE.
        alias=None,
        identity=None,
    )
    _attribute_order = (
        "mode",
        "alias",
        "identity",
    )
    assert set(_attribute_order) == set(attributes)

    def __init__(self):
        """Customise ValueList for playing mode data."""
        super().__init__()
        self.mode = None
        self.alias = None
        self.identity = None

    def empty(self):
        """(Re)Initialize value attribute."""
        self.mode = None
        self.alias = None
        self.identity = None

    def alias_index_key(self):
        """Return the key for the modealias index."""
        return repr(self.mode)

    def load_alias_index_key(self, value):
        """Bind attributes for the modealias index to items in value."""
        (self.mode,) = literal_eval(value)

    def pack(self):
        """Delegate to generate playing mode data then add index data.

        The modealias index will have the mode name and other descriptive
        detail as it's value, from the alias_index_key() method.

        The modeidentity index will have either the identity number given
        when the record was created (identity attribute), or the identity
        number of the playing mode record which this record currently
        aliases (alias attribute).

        """
        val = super().pack()
        index = val[1]
        index[filespec.MODE_ALIAS_FIELD_DEF] = [self.alias_index_key()]
        index[filespec.MODE_IDENTITY_FIELD_DEF] = [self.alias]
        return val


class ModeDBrecord(Record):
    """Customise Record with ModeDBkey and ModeDBvalue by default."""

    def __init__(self, keyclass=ModeDBkey, valueclass=ModeDBvalue):
        """Delegate with keyclass and valueclass arguments."""
        super().__init__(keyclass, valueclass)

    def get_keys(self, datasource=None, partial=None):
        """Override, return [(key, value)] for datasource or []."""
        try:
            if partial is not None:
                return []
            srkey = datasource.dbhome.encode_record_number(self.key.pack())
            if datasource.primary:
                return [(srkey, self.srvalue)]
            dbname = datasource.dbname
            if dbname == filespec.MODE_ALIAS_FIELD_DEF:
                return [(self.value.alias_index_key(), srkey)]
            if dbname == filespec.MODE_IDENTITY_FIELD_DEF:
                return [(self.value.alias, srkey)]
            return []
        except:  # pycodestyle E722: pylint is happy with following 'raise'.
            if datasource is None:
                return []
            raise


class ModeDBImporter(ModeDBrecord):
    """Extend with methods to import multiple game headers from PGN files."""

    def copy_mode_names_from_games(
        self,
        database,
        reporter=None,
        quit_event=None,
        **kwargs,
    ):
        """Return True if copy mode names from games file succeeds.

        quit_event allows the import to be interrupted by passing an Event
        instance which get queried after processing each game.
        kwargs soaks up arguments not used in this method.

        """
        del kwargs
        if reporter is not None:
            reporter.append_text("Copy playing mode names from games.")
        cursor = database.database_cursor(
            filespec.GAME_FILE_DEF, filespec.GAME_MODE_FIELD_DEF
        )
        value = self.value
        db_segment_size = SegmentSize.db_segment_size
        game_count = 0
        onfile_count = 0
        copy_count = 0
        prev_record = None
        while True:
            record = cursor.next()
            if record is None:
                break
            this_record = record[0]
            if prev_record == this_record:
                continue
            game_count += 1
            prev_record = this_record
            value.mode = this_record
            alias = value.alias_index_key()
            if quit_event and quit_event.is_set():
                if reporter is not None:
                    reporter.append_text_only("")
                    reporter.append_text("Copy stopped.")
                return False
            if database.recordlist_key(
                filespec.MODE_FILE_DEF,
                filespec.MODE_ALIAS_FIELD_DEF,
                key=database.encode_record_selector(alias),
            ).count_records():
                onfile_count += 1
                continue
            copy_count += 1
            pid = identity.get_next_mode_identity_value_after_allocation(
                database
            )
            value.alias = pid
            value.identity = pid
            self.key.recno = None
            self.put_record(database, filespec.MODE_FILE_DEF)
            if int(pid) % db_segment_size == 0:
                # Need the cursor wrapping in berkeleydb, bsddb3, db_tkinter
                # and lmdb too.
                cursor.close()
                database.commit()
                database.start_transaction()
                cursor = database.database_cursor(
                    filespec.GAME_FILE_DEF, filespec.GAME_MODE_FIELD_DEF
                )
                cursor.setat(record)

                if reporter is not None:
                    reporter.append_text(
                        "".join(
                            (
                                "Mode ",
                                value.mode,
                                " is record ",
                                str(self.key.recno),
                            )
                        )
                    )
        if reporter is not None:
            reporter.append_text_only("")
            reporter.append_text(
                "".join(
                    (
                        str(copy_count),
                        " modes added to database.",
                    )
                )
            )
            reporter.append_text_only(
                "".join(
                    (
                        str(onfile_count),
                        " modes already on database.",
                    )
                )
            )
            reporter.append_text_only(
                "".join(
                    (
                        str(game_count),
                        " game references processed.",
                    )
                )
            )
            reporter.append_text_only("")
        return True

    def count_mode_names_to_be_copied_from_games(
        self,
        database,
        reporter=None,
        quit_event=None,
        **kwargs,
    ):
        """Return number of mode names in games file but not modes file.

        quit_event allows the import to be interrupted by passing an Event
        instance which get queried after processing each game.
        kwargs soaks up arguments not used in this method.

        """
        del kwargs
        if reporter is not None:
            reporter.append_text("Count mode names to be copied from games.")
        cursor = database.database_cursor(
            filespec.GAME_FILE_DEF, filespec.GAME_MODE_FIELD_DEF
        )
        value = self.value
        prev_record = None
        count = 0
        while True:
            record = cursor.next()
            if record is None:
                break
            this_record = literal_eval(record[0])
            if prev_record == this_record:
                continue
            prev_record = this_record
            (value.mode,) = this_record
            alias = value.alias_index_key()
            if quit_event and quit_event.is_set():
                if reporter is not None:
                    reporter.append_text_only("")
                    reporter.append_text("Count stopped.")
                return None
            if database.recordlist_key(
                filespec.MODE_FILE_DEF,
                filespec.MODE_ALIAS_FIELD_DEF,
                key=database.encode_record_selector(alias),
            ).count_records():
                continue
            count += 1
        if reporter is not None:
            reporter.append_text(
                str(count) + " mode names to be copied from games."
            )
        return count
