# population.py
# Copyright 2024 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Population performance calculation from results in selected events.

Derived from performances.py in version 1.3.4 of chesscalc.

"""
import copy

from . import performancerecord
from . import filespec
from . import person
from . import constants

_RESULT_TO_REWARD = {
    "1-0": {0: 1, 1: -1},
    "1/2-1/2": {0: 0, 1: 0},
    "0-1": {0: -1, 1: 1},
}


class Population:
    """Calculate performances of a player population from selected games."""

    def __init__(
        self,
        database,
        playerset,
        games,
        measure=50,
    ):
        """Initialise population data."""
        self.iterations = 0
        self.high_performance = None
        self.persons = {}
        self.measure = measure
        persons = self.persons
        encode_record_selector = database.encode_record_selector
        database_cursor = database.database_cursor
        recordlist_key = database.recordlist_key
        person_record = performancerecord.PlayerDBrecord()
        game_record = performancerecord.GameDBrecord()
        person_cursor = database_cursor(
            filespec.PLAYER_FILE_DEF, None, recordset=playerset
        )
        person_cursor.recordset.reset_current_segment()
        while True:
            record = person_cursor.next()
            if record is None:
                break
            person_record.load_record(record)
            player_identity = person_record.value.identity
            player_alias = person_record.value.alias_index_key()
            person_games = recordlist_key(
                filespec.GAME_FILE_DEF,
                filespec.GAME_PERSON_FIELD_DEF,
                key=encode_record_selector(player_identity),
            )
            persons[player_identity] = person.Person(
                player_identity, person_record.value.name
            )
            opponents = persons[player_identity].opponents
            person_games &= games
            game_cursor = database_cursor(
                filespec.GAME_FILE_DEF, None, recordset=person_games
            )
            while True:
                record = game_cursor.next()
                if record is None:
                    break
                game_record.load_record(record)
                result = game_record.value.headers[constants.TAG_RESULT]
                for side, game_player in enumerate(
                    (
                        game_record.value.black_key(),
                        game_record.value.white_key(),
                    )
                ):
                    if game_player == player_alias:
                        continue
                    game_opponent = recordlist_key(
                        filespec.PLAYER_FILE_DEF,
                        filespec.PERSON_ALIAS_FIELD_DEF,
                        key=encode_record_selector(game_player),
                    )
                    game_opponent_cursor = database_cursor(
                        filespec.PLAYER_FILE_DEF,
                        None,
                        recordset=game_opponent,
                    )
                    record = game_opponent_cursor.first()
                    if record is None:
                        continue
                    person_record.load_record(record)
                    value = person_record.value
                    if value.alias == player_identity:
                        continue
                    if value.alias == value.identity:
                        persons[player_identity].add_reward(
                            _RESULT_TO_REWARD[result][side],
                            measure,
                        )
                        opponents.append(value.identity)
                        continue
                    game_opponent = recordlist_key(
                        filespec.PLAYER_FILE_DEF,
                        filespec.PLAYER_UNIQUE_FIELD_DEF,
                        key=encode_record_selector(person_record.value.alias),
                    )
                    game_opponent_cursor = database_cursor(
                        filespec.PLAYER_FILE_DEF,
                        None,
                        recordset=game_opponent,
                    )
                    record = game_opponent_cursor.first()
                    if record is None:
                        continue
                    person_record.load_record(record)
                    persons[player_identity].add_reward(
                        _RESULT_TO_REWARD[result][side],
                        measure,
                    )
                    opponents.append(value.identity)

    def __deepcopy__(self, memo):
        """Return deep copy of self."""
        newcopy = empty_copy(self)
        newcopy.iterations = 0
        newcopy.high_performance = None
        newcopy.persons = copy.deepcopy(self.persons, memo)
        newcopy.measure = self.measure
        return newcopy

    def do_iterations_until_stable(self, delta=0.000000000001):
        """Iterate until all performances vary by less tham delta.

        Performances in an iteration are compared with the previous iteration.

        """
        while True:
            self.iterations += 1
            self.iterate_performance()
            for player in self.persons.values():
                if not player.is_performance_stable(delta):
                    break
            else:
                return

    def iterate_performance(self):
        """Do one iteration of the performance calculation."""
        for player in self.persons.values():
            player.set_points()
        for player in self.persons.values():
            for opponent in player.opponents:
                player.add_points(self.persons[opponent].performance)
        for player in self.persons.values():
            player.calculate_performance()

    def set_high_performance(self):
        """Note high performance in population."""
        high_performance = 0
        for player in self.persons.values():
            high_performance = max(high_performance, player.performance)
        self.high_performance = high_performance


def empty_copy(obj):
    """Return an empty instance of obj."""

    class EmptyCopy(obj.__class__):
        """Empty subclass which does not invoke superclass __init__()."""

        def __init__(self):
            pass

    newcopy = EmptyCopy()
    newcopy.__class__ = obj.__class__
    return newcopy