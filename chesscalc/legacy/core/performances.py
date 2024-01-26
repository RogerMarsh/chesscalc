# performances.py
# Copyright 2012 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Player performance calculation from results in selected events."""

import math
import collections

_REWARD_TO_RESULT = {1: 1, 0: 0.5, -1: 0}
_REVERSE_ACTUAL = {1: 0, 0.5: 0.5, 0: 1}

MAX_GRADE = "Max Grade"
MAX_INITIAL_PERF = "Max Initial Performance"
MAX_PERF = "Max Performance"
MAX_PERF_CALC = "Max Performance Calculated"
MEAN_DIFF_GAP_SCORE_PREDICTION = "Mean Diff Score Prediction for Gap"
MEAN_DIFF_SCORE_PREDICTION = "Mean Diff Score Prediction"
MEAN_GRADE = "Mean Grade"
MEAN_INITIAL_PERF = "Mean Initial Performance"
MEAN_PERF = "Mean Performance"
MEAN_PERF_CALC = "Mean Performance Calculated"
MEDIAN_GRADE = "Median Grade"
MEDIAN_INITIAL_PERF = "Median Initial Performance"
MEDIAN_PERF = "Median Performance"
MEDIAN_PERF_CALC = "Median Performance Calculated"
MIN_GRADE = "Min Grade"
MIN_INITIAL_PERF = "Min Initial Performance"
MIN_PERF = "Min Performance"
MIN_PERF_CALC = "Min Performance Calculated"
STDEV_SCORE_PREDICTION = "Stdev Score Prediction"
STDEV_GAP_SCORE_PREDICTION = "Stdev Score Prediction for Gaps"
SUM_GAP_PREDICTION = "Sum Gap Prediction"
SUM_GAP_GAMES = "Sum Gap Games"
SUM_GAP_SCORE = "Sum Gap Score"
SUM_GAP_PREDICTION_GRADE = "Sum Gap Prediction Grade"
SUM_GAP_GAMES_GRADE = "Sum Gap Games Grade"
SUM_GAP_SCORE_GRADE = "Sum Gap Score Grade"
SUM_GAP_PREDICTION_CALC = "Sum Gap Prediction Calculated"
SUM_GAP_GAMES_CALC = "Sum Gap Games Calculated"
SUM_GAP_SCORE_CALC = "Sum Gap Score Calculated"
SUM_GRADE = "Sum Grade"
SUM_PERF = "Sum Performance"
SUM_PERF_CALC = "Sum Performance Calculated"
WEIGHTED_SUM_GRADE = "Weighted Sum Grade"
SUM_INITIAL_PERF = "Sum Initial Performance"
WEIGHTED_SUM_INITIAL_PERF = "Weighted Sum Initial Performance"
WEIGHTED_SUM_PERF = "Weighted Sum Performance"
WEIGHTED_SUM_PERF_CALC = "Weighted Sum Performance Calculated"
SUM_PREDICTION = "Sum Prediction"
SUM_HALF_GAMES = "Sum Half-Games"
SUM_SCORE = "Sum Score"


class Performances:
    """Player performances in a set of events."""

    def __init__(self):
        """Initialise calculation data from database records for events."""
        super().__init__()
        self.games = None
        self.players = None
        self.game_opponent = None
        self.opponents = None
        self.populations = None  # list of distinct populations
        self.subpopulations = None
        self.removed = None
        self.statistics = None
        self.discarded_populations = None
        self.discarded_players = None

    def split_players_into_populations(self, allplayers):
        """Return players split into distinct populations.

        Each player in a population is connected to all other players in the
        population by at least one path stepping via opponents in a game.

        """
        players = set(allplayers)
        populations = []
        while len(players) > 0:
            populations.append([])
            subpop = [[players.pop()]]
            populations[-1].extend(subpop[-1])
            while len(subpop[-1]) > 0:
                opps = []
                for person in subpop[-1]:
                    for game in self.players[person]:
                        opponent = self.game_opponent[game][person]
                        if opponent in players:
                            opps.append(opponent)
                            players.remove(opponent)
                subpop.append(opps)
                populations[-1].extend(opps)
        return populations

    def find_distinct_populations(self):
        """Set self.populations as the distinct populations."""
        if self.players is None:
            return
        self.populations = self.split_players_into_populations(self.players)

    def _find_population_fracture_point(self, population):
        """Return pre-fracture sub-population and post-fracture populations.

        Players in a population will play varying numbers of opponents and
        games.  Find the fracture point by ignoring players with one, two,
        and so on, opponents in turn until the population splits into two or
        more distinct populations.

        The idea is that populations from which players with a higher number
        of opponents can be removed without fracturing give better performance
        numbers than those where the number is lower.

        """
        if self.opponents is None:
            return None
        subpopulations = [[list(population)]]
        players = set(population)
        removed = []
        while len(players) > 0:
            removed.append(
                [
                    p
                    for p in players
                    if len(self.opponents[p]) == len(subpopulations)
                ]
            )
            for person in removed[-1]:
                players.remove(person)
            subpopulations.append(self.split_players_into_populations(players))
            if len(subpopulations[-1]) > 1:
                break
        return subpopulations, removed

    def find_population_fracture_points(self):
        """Set sub-populations as players removed until population splits."""
        if self.opponents is None:
            return
        self.subpopulations = []
        self.removed = []
        for population in self.populations:
            item = self._find_population_fracture_point(population)
            if item is not None:
                self.subpopulations.append(item[0])
                self.removed.append(item[1])

    def get_events(self, games, players, game_opponent, opponents):
        """Initialise calculation data from database records for events."""
        if self.games is not None:
            return
        self.games = games
        self.players = players
        self.game_opponent = game_opponent
        self.opponents = opponents

    def get_largest_population(self):
        """Trim the games to match the largest connected population."""
        if len(self.populations) < 2:
            return
        pops = sorted([(len(p), p) for p in self.populations])
        self.discarded_populations = [p[-1] for p in pops[:-1]]
        self.populations = pops[-1][-1]
        pops = set()
        for item in self.discarded_populations:
            pops.update(item)
        self.discarded_players = set()
        for population in pops:
            for item in self.players[population]:
                if item in self.games:
                    del self.games[item]
                if item in self.game_opponent:
                    del self.game_opponent[item]
            self.discarded_players.add(population)
            del self.players[population]
            del self.opponents[population]

    def is_connected_graph_of_opponents_a_tree(self):
        """Return True if the graph, assumed to be connected, is a tree."""
        edges = sum(len(opp) for opp in self.opponents.values()) // 2
        return bool(edges == len(self.opponents) - 1)

    def cycle_state_connected_graph_of_opponents(self):
        """Return True if graph is a tree, False if 3-cycle exists, else None.

        Iteration converges on a single set of values or an oscillation between
        two sets of values, assuming a connected graph of opponents.

        The iteration oscillates if the graph of opponents is a tree.

        The iteration converges if the graph of opponents contains at least one
        3-cycle: A plays B, B plays C, C plays A.

        The iteration may converge or oscillate if the shortest n-cycle in the
        graph of opponents has n > 3.  It depends on the results of the games
        between players in the cycle.  All cases for a 3-cycle were tried where
        exactly three games were played, and sufficient cases were tried for a
        4-cycle to establish both convergence and oscillation occur.

        A way of forcing convergence is to add a 3-ring to a node, preferably
        one with a single edge: (N draw A, A draw B, B draw N) where A and B
        are the added nodes and N is the existing node.

        """
        if self.is_connected_graph_of_opponents_a_tree():
            return True
        sopps = self.opponents
        for player, opponents in sopps.items():
            for person in opponents:
                for opp in sopps[person]:
                    if player != opp:
                        if player in sopps[opp]:
                            return False
        return None


class Gap:
    """Actual and expected results for a performance differences."""

    def __init__(self, actual, expected):
        """Initialise gap data for actual and expected scores."""
        super().__init__()
        self.count = 1
        self.actual = actual
        self.expected = expected

    def add(self, actual, expected):
        """Add actual and expected scores for game to gap data."""
        self.count += 1
        self.actual += actual
        self.expected += expected


class Person:
    """Player details and calculation answers."""

    def __init__(self, initialperformance):
        """Initialise calculation data.

        If initialperformance is not None the value is used as the player's
        performance in all calculations of performance but iteration[0] is
        still the result of the most recent performance calculation.

        """
        super().__init__()
        self.reward = 0
        self.game_count = 0
        self.initial_performance = initialperformance
        if initialperformance is None:
            self.iteration = [0]
        else:
            self.iteration = [initialperformance]
        self.points = 0
        self.grade_points = 0
        self.predicted_score = 0
        self.predicted_score_initial = 0
        self.predicted_score_grade = 0
        self.score = 0
        self.grade = 0

    def add_grade_points(self, points):
        """Add opponent's performance to grade points."""
        self.grade_points += points

    def add_points(self, points):
        """Add opponent's performance to points."""
        self.points += points

    def add_predicted_score_grade(self, predicted_score):
        """Increment predicted score using calculated grade."""
        self.predicted_score_grade += predicted_score

    def add_predicted_score(self, predicted_score):
        """Increment predicted score using calculated performance."""
        self.predicted_score += predicted_score

    def add_predicted_score_initial(self, predicted_score):
        """Increment predicted score using initial performance if available."""
        self.predicted_score_initial += predicted_score

    def add_reward(self, reward, measure):
        """Increment total reward, total score and game count."""
        self.reward += reward * measure
        self.game_count += 1
        self.score += _REWARD_TO_RESULT[reward]

    def calculate_grade(self):
        """Calculate and set player's grade."""
        self.grade = float(self.grade_points + self.reward) / self.game_count

    def calculate_performance(self):
        """Calculate and set player's performance."""
        self.iteration.insert(
            0, float(self.points + self.reward) / self.game_count
        )
        del self.iteration[3:]

    def get_grade(self):
        """Return player's grade."""
        if self.initial_performance is None:
            return self.grade
        return self.initial_performance

    def get_calculated_performance(self):
        """Return player's calculated performance."""
        return self.iteration[0]

    def get_initial_performance(self):
        """Return player's initial performance."""
        if self.initial_performance is None:
            return 0
        return self.initial_performance

    def get_performance(self):
        """Return player's performance for use in next ieration."""
        if self.initial_performance is None:
            return self.iteration[0]
        return self.initial_performance

    def get_score(self):
        """Return player's actual total score."""
        return self.score

    def is_performance_constant(self):
        """Return True if performance is fixed for iteration calculations."""
        return self.initial_performance is not None

    def is_performance_stable(self, delta):
        """Return True if performance is fixed for iteration calculations."""
        if self.initial_performance is not None:
            return True
        for count, number in enumerate(self.iteration[1:]):
            if abs(number - self.iteration[count]) > delta:
                break
        else:
            return True
        return False

    def set_points(self, points=0):
        """Initialise sum of opponent's performance to points."""
        self.points = points


class Calculation:
    """Player performances calculated from a collection of results."""

    def __init__(
        self,
        population,
        games,
        opponents,
        initialperformance=None,
        iterations=10,
        limit=40,
        measure=50,
    ):
        """Initialise calculation data."""
        super().__init__()
        if initialperformance is None:
            initialperformance = {}
        self.iterations = iterations
        self.opponents = opponents
        self.games = games
        self.popgames = set()
        self.persons = {}
        self.gap = {}
        self.gap_grade = {}
        self.gap_initial = {}
        self.statistics = None
        self.limit = limit
        self.measure = measure
        self.span = measure * 2
        persons = self.persons
        for game, result in games.items():
            for player in result:
                if player not in population:
                    break
            else:
                self.popgames.add(game)
                for player, reward in result.items():
                    if player not in persons:
                        persons[player] = Person(
                            initialperformance.get(player)
                        )
                    persons[player].add_reward(reward, measure)

    def do_iterations(self, calculation=None, finalcalculation=None):
        """Do iterations with calculation and final_calculation functions."""
        if self.games is None:
            return
        for _ in range(self.iterations):
            self.iterate_performance(calculation)
        if isinstance(finalcalculation, collections.abc.Callable):
            self.iterate_performance(finalcalculation)
        self.process_all_results(self.grade_difference)
        for player in self.persons.values():
            player.calculate_grade()
        self.process_all_results(self.performance_prediction)
        for key in self.popgames:
            self.result_prediction(self.games[key])

    def get_statistics(self):
        """Return dict of performance statistics."""
        if self.statistics is not None:
            return self.statistics.copy()

        stat = {}
        stat[MAX_GRADE] = max(p.get_grade() for p in self.persons.values())
        stat[MAX_INITIAL_PERF] = max(
            p.get_initial_performance() for p in self.persons.values()
        )
        stat[MAX_PERF] = max(
            p.get_performance() for p in self.persons.values()
        )
        stat[MAX_PERF_CALC] = max(
            p.get_calculated_performance() for p in self.persons.values()
        )
        stat[MEAN_DIFF_GAP_SCORE_PREDICTION] = mean(
            [
                abs(g.actual - g.expected)
                for g in self.gap.values()
                if g.count > 0
            ]
        )
        stat[MEAN_DIFF_SCORE_PREDICTION] = mean(
            [
                abs(p.get_score() - p.predicted_score)
                for p in self.persons.values()
            ]
        )
        stat[MEAN_GRADE] = mean([p.get_grade() for p in self.persons.values()])
        stat[MEAN_INITIAL_PERF] = mean(
            [p.get_initial_performance() for p in self.persons.values()]
        )
        stat[MEAN_PERF] = mean(
            [p.get_performance() for p in self.persons.values()]
        )
        stat[MEAN_PERF_CALC] = mean(
            [p.get_calculated_performance() for p in self.persons.values()]
        )
        stat[MEDIAN_GRADE] = median(
            [p.get_grade() for p in self.persons.values()]
        )
        stat[MEDIAN_INITIAL_PERF] = mean(
            [p.get_initial_performance() for p in self.persons.values()]
        )
        stat[MEDIAN_PERF] = median(
            [p.get_performance() for p in self.persons.values()]
        )
        stat[MEDIAN_PERF_CALC] = median(
            [p.get_calculated_performance() for p in self.persons.values()]
        )
        stat[MIN_GRADE] = min(p.get_grade() for p in self.persons.values())
        stat[MIN_INITIAL_PERF] = min(
            p.get_initial_performance() for p in self.persons.values()
        )
        stat[MIN_PERF] = min(
            p.get_performance() for p in self.persons.values()
        )
        stat[MIN_PERF_CALC] = min(
            p.get_calculated_performance() for p in self.persons.values()
        )
        stat[STDEV_SCORE_PREDICTION] = stdev(
            [
                abs(p.get_score() - p.predicted_score)
                for p in self.persons.values()
            ]
        )
        stat[STDEV_GAP_SCORE_PREDICTION] = stdev(
            [
                abs(g.actual - g.expected)
                for g in self.gap.values()
                if g.count > 0
            ]
        )
        stat[SUM_GAP_PREDICTION] = sum(
            g.expected for g in self.gap_initial.values()
        )
        stat[SUM_GAP_GAMES] = sum(g.count for g in self.gap_initial.values())
        stat[SUM_GAP_SCORE] = sum(g.actual for g in self.gap_initial.values())
        stat[SUM_GAP_PREDICTION_GRADE] = sum(
            g.expected for g in self.gap_grade.values()
        )
        stat[SUM_GAP_GAMES_GRADE] = sum(
            g.count for g in self.gap_grade.values()
        )
        stat[SUM_GAP_SCORE_GRADE] = sum(
            g.actual for g in self.gap_grade.values()
        )
        stat[SUM_GAP_PREDICTION_CALC] = sum(
            g.expected for g in self.gap.values()
        )
        stat[SUM_GAP_GAMES_CALC] = sum(g.count for g in self.gap.values())
        stat[SUM_GAP_SCORE_CALC] = sum(g.actual for g in self.gap.values())
        stat[SUM_GRADE] = sum(p.get_grade() for p in self.persons.values())
        stat[SUM_PERF] = sum(
            p.get_performance() for p in self.persons.values()
        )
        stat[SUM_PERF_CALC] = sum(
            p.get_calculated_performance() for p in self.persons.values()
        )
        stat[WEIGHTED_SUM_GRADE] = sum(
            p.game_count * p.get_grade() for p in self.persons.values()
        )
        stat[SUM_INITIAL_PERF] = sum(
            p.get_initial_performance() for p in self.persons.values()
        )
        stat[WEIGHTED_SUM_INITIAL_PERF] = sum(
            p.game_count * p.get_initial_performance()
            for p in self.persons.values()
        )
        stat[WEIGHTED_SUM_PERF] = sum(
            p.game_count * p.get_performance() for p in self.persons.values()
        )
        stat[WEIGHTED_SUM_PERF_CALC] = sum(
            p.game_count * p.get_calculated_performance()
            for p in self.persons.values()
        )
        stat[SUM_PREDICTION] = sum(
            p.predicted_score for p in self.persons.values()
        )
        stat[SUM_HALF_GAMES] = sum(p.game_count for p in self.persons.values())
        stat[SUM_SCORE] = sum(p.get_score() for p in self.persons.values())
        self.statistics = stat
        return self.statistics.copy()

    def grade_difference(self, game):
        """Calculate grade: self.limit on difference is implied."""
        for key, value in game.items():
            operf = self.persons[value].get_performance()
            pperf = self.persons[key].get_performance()
            if pperf - operf > self.limit:
                self.persons[key].add_grade_points(pperf - self.limit)
            elif operf - pperf > self.limit:
                self.persons[key].add_grade_points(pperf + self.limit)
            else:
                self.persons[key].add_grade_points(operf)

    def iterate_performance(self, calculation=None):
        """Do one iteration of the performance calculation."""
        if not isinstance(calculation, collections.abc.Callable):
            calculation = self.performance_difference
        for player in self.persons.values():
            player.set_points()
        self.process_all_results(calculation)
        for player in self.persons.values():
            player.calculate_performance()

    def performance_difference(self, game):
        """Calculate game performances without a limit on difference."""
        for player, opponent in game.items():
            self.persons[player].add_points(
                self.persons[opponent].get_performance()
            )

    def performance_difference_limited(self, game):
        """Calculate game performances with self.limit on difference."""
        for key, value in game.items():
            operf = self.persons[value].get_performance()
            pperf = self.persons[key].get_performance()
            if pperf - operf > self.limit:
                self.persons[key].add_points(pperf - self.limit)
            elif operf - pperf > self.limit:
                self.persons[key].add_points(pperf + self.limit)
            else:
                self.persons[key].add_points(operf)

    def process_all_results(self, process):
        """Do process on games where both players are in population."""
        if self.opponents is None:
            return
        for popgame in self.popgames:
            process(self.opponents[popgame])

    def _performance_prediction(self, get_player, get_opponent, add):
        """Add predicted score into entry using add method."""
        gap = get_player() - get_opponent()
        if gap > self.measure:
            add(1)
        elif -gap <= self.measure:
            add((gap + self.measure) / self.span)

    def performance_prediction(self, game):
        """Calculate predicted scores from calculated performances."""
        for player, opponent in [
            (self.persons[p], self.persons[o]) for p, o in game.items()
        ]:
            self._performance_prediction(
                player.get_calculated_performance,
                opponent.get_calculated_performance,
                player.add_predicted_score,
            )
            self._performance_prediction(
                player.get_performance,
                opponent.get_performance,
                player.add_predicted_score_initial,
            )
            self._performance_prediction(
                player.get_grade,
                opponent.get_grade,
                player.add_predicted_score_grade,
            )

    def _result_prediction(self, actual, gap, gaps):
        """Add actual and expected result for gap into gaps entry for gap."""
        if gap > self.measure:
            expected = 1
        elif -gap > self.measure:
            actual = _REVERSE_ACTUAL[actual]
            gap = -gap
            expected = 1
        elif gap < 0:
            actual = _REVERSE_ACTUAL[actual]
            gap = -gap
            expected = (gap + self.measure) / self.span
        else:
            expected = (gap + self.measure) / self.span
        try:
            gaps[int(min(gap, self.measure + 1))].add(actual, expected)
        except KeyError:
            gaps[int(min(gap, self.measure + 1))] = Gap(actual, expected)

    def result_prediction(self, game):
        """Calculate actual and expected scores for performance differences.

        Calculation is from point of view of player with higher performance
        number.  So 1 >= expected score in any game >= 0.5.

        """
        (player, reward), (opponent, gash) = [
            (self.persons[p], game[p]) for p in game.keys()
        ]
        del gash
        actual = _REWARD_TO_RESULT[reward]
        # self.gap and self.gap_initial will have different values if
        # initial_performance is not None for some persons
        self._result_prediction(
            actual,
            (
                player.get_calculated_performance()
                - opponent.get_calculated_performance()
            ),
            self.gap,
        )
        self._result_prediction(
            actual,
            player.get_performance() - opponent.get_performance(),
            self.gap_initial,
        )
        self._result_prediction(
            actual, player.get_grade() - opponent.get_grade(), self.gap_grade
        )

    def do_iterations_until_stable(self, delta=0.000000000001, cycles=None):
        """Iterate until all performances vary by less tham delta.

        Performances in an iteration are compared with the previous iteration.

        A cycles argument which is not None allows iterations to continue
        until the condition on deleta is met.  Otherwise the number of
        iterations is limited by self.iterations.

        """
        if self.games is None:
            return None
        cycle_iterations = self.iterations * 2
        iterations = 0
        while True:
            iterations += 1
            self.iterate_performance()
            for person in self.persons.values():
                if not person.is_performance_stable(delta):
                    break
            else:
                return iterations, delta, True
            if cycles is None:
                if iterations > cycle_iterations:
                    return iterations, delta, False


class Distribution:
    """Game results partitioned by performance difference between players.

    Partition a set of games against the performance calculation for a set of
    games used as a reference.  Games are included only if both players are in
    the reference population.  Partitioning is done using one or more intervals
    and the results are cached.  The interval is used to pick 'all games where
    the player's performances differ by between base and base plus interval
    points' for whatever bases are needed for the games.

    """

    def __init__(self, players, games):
        """Initialise distribution data."""
        super().__init__()
        if isinstance(players, Calculation):
            players = players.persons
        players = {
            k: v.get_calculated_performance() if isinstance(v, Person) else v
            for k, v in players.items()
        }
        if isinstance(games, Calculation):
            games = {
                k: v
                for k, v in games.games.items()
                if len({p for p in v if p in players}) == 2
            }
        gameplayers = set()
        for key in games.values():
            gameplayers.update(key)
        players = {k: v for k, v in players.items() if k in gameplayers}
        self.players = players
        self.games = games
        self.distributions = {}

    def calculate_distribution(self, interval):
        """Calculate and cache the result distribution using interval."""
        if interval in self.distributions:
            return
        distribution = {}
        for game in self.games.items():
            playerone, playertwo = game[-1]
            bucket = int(
                abs(self.players[playerone] - self.players[playertwo])
                // interval
            )
            if bucket not in distribution:
                distribution[bucket] = Interval(bucket, interval)
            distribution[bucket].add_result(game, self.players)
        self.distributions[interval] = distribution


class Interval:
    """Accumulate results for a performance difference.

    Results are recorded from the point of view of the player with the higher
    performance.  Performance difference is >= base and < base + width.

    """

    def __init__(self, bucket, width):
        """Initialise interval description."""
        super().__init__()
        self.base = bucket * width
        self.width = width
        self.wins = 0
        self.draws = 0
        self.losses = 0

    def add_result(self, game, reference):
        """Increment the appropriate win, draw, loss counter for result."""
        item1, item2 = ((k, v) for k, v in game[-1].items())
        if item1[1] == 0:
            self.draws += 1
        elif reference[item1[0]] >= reference[item2[0]]:
            if item1[1] > 0:
                self.wins += 1
            else:
                self.losses += 1
        elif item1[1] > 0:
            self.losses += 1
        else:
            self.wins += 1


# PopulationMap may benefit from implementation using the Recordset and List
# manipulation methods provided by the DPT database engine (www.dptoolkit.com).
# At large scales such implementation may be necessary to perform the algorithm
# within reasonable resource constraints (time and/or memory).


class PopulationMap:
    """Partition a population into core, link, and remainder populations.

    Partitioning is done using the number of edges attached to a node.

    The core populations are those with more than a given number of edges
    attached to a node.  The link populations are the nodes with at least one
    edge to a node in the core and at least one edge to a node not in the core.
    The remainder populations are the nodes with no edges to a node in the
    core.  The nodes in the link and remainder populations are attached to at
    most the given number of edges.

    """

    def __init__(self, performances, partitioning_edge_count=None):
        """Initialise population map."""
        super().__init__()
        if not isinstance(partitioning_edge_count, int):
            self.edges = min(
                max(0, len(performances.subpopulations[-1]) - 1),
                len(performances.removed[-1]),
            )
        elif partitioning_edge_count < 0:
            self.edges = min(
                max(0, len(performances.subpopulations[-1]) - 1),
                len(performances.removed[-1]),
            )
        else:
            self.edges = min(
                partitioning_edge_count,
                max(0, len(performances.subpopulations[-1]) - 1),
                len(performances.removed[-1]),
            )
        # Just the bits of performances instance needed (for now)
        self._subpopulations = performances.subpopulations[-1][self.edges]
        self._removed = performances.removed[-1][: self.edges]
        self._opponents = performances.opponents
        # Place holders for population map
        self._core_populations = None
        self._link_populations = None
        self._remainder_populations = None
        # Temporary reference to performances deleted by rebuild_populations
        self.__performances = performances
        # Rebuilt population information including links between them.
        self._core_players = None
        self._core_opps_all = None
        self._core_opps_core = None
        self._core_opps_link = None
        self._link_players = None
        self._link_opps_all = None
        self._link_opps_link = None
        self._link_opps_rest = None
        self._link_opps_core = None
        self._rest_players = None
        self._rest_opps_all = None
        self._rest_opps_rest = None
        self._rest_opps_link = None
        # Rebuilt population information available
        self._population_information = False

    def rebuild_populations(self):
        """Rebuild populations as core, link, and remainder populations."""
        if self.__performances is None:
            return
        perf = self.__performances
        core_populations = [set(s) for s in self._subpopulations]
        link_players = [set(r) for r in self._removed]
        while True:
            # Restore removed players to population if all player's opponents
            # are in population.
            # Repeat until a pass is done without restoring any players.
            recombine = [set() for r in range(len(core_populations))]
            for item in link_players:
                for element in list(item):
                    for index, value in enumerate(core_populations):
                        if len(self._opponents[element] - value) == 0:
                            recombine[index].add(element)
                            item.remove(element)
                            break
            for index, value in enumerate(recombine):
                core_populations[index].update(value)
            if not sum(len(rc) for rc in recombine):
                break
        # Remove players who do not have an opponent in core_populations
        # from link_players and repartition these players into subpopulations.
        # But no need to find fracture point (if not already fractured).
        repartition = set()
        for item in link_players:
            for element in list(item):
                for value in core_populations:
                    if len(value - self._opponents[element]) != len(value):
                        break
                else:
                    repartition.add(element)
                    item.remove(element)
        remainder_populations = perf.split_players_into_populations(
            repartition
        )
        # Repartition remaining players in link_players into subpopulations.
        # But no need to find fracture point (if not already fractured).
        link_repartition = set()
        for item in link_players:
            link_repartition.update(item)
        link_populations = perf.split_players_into_populations(
            link_repartition
        )
        # Save state
        self._core_populations = core_populations
        self._link_populations = link_populations
        self._remainder_populations = remainder_populations
        self.__performances = None

    @property
    def population_information(self):
        """Return dict of core, link, and remainder population statistics."""
        if not self._population_information:
            self._calculate_population_information()
            self._population_information = True
        return (
            self._core_players,
            self._core_opps_all,
            self._core_opps_core,
            self._core_opps_link,
            self._link_players,
            self._link_opps_all,
            self._link_opps_link,
            self._link_opps_rest,
            self._link_opps_core,
            self._rest_players,
            self._rest_opps_all,
            self._rest_opps_rest,
            self._rest_opps_link,
        )

    def _calculate_population_information(self):
        """Calculate core, link, and remainder population information."""

        def calc_inf(players, opps_all, opps_own, key, src_pop):
            opps = self._opponents
            players[key] = len(src_pop)
            opps_all[key] = sum(len(opps[p]) for p in src_pop)
            total = sum(
                len([o for o in opps[p] if o in src_pop]) for p in src_pop
            )
            if total:
                opps_own[key] = total

        def calc_xref(inf, key, ppop, xref):
            opps = self._opponents
            inf[key] = {}
            for index, item in enumerate(xref):
                total = sum(
                    len([o for o in opps[p] if o in ppop]) for p in item
                )
                if total:
                    inf[key][index] = total

        core_players = {}
        core_opps_all = {}
        core_opps_core = {}
        core_opps_link = {}
        link_players = {}
        link_opps_all = {}
        link_opps_link = {}
        link_opps_rest = {}
        link_opps_core = {}
        rest_players = {}
        rest_opps_all = {}
        rest_opps_rest = {}
        rest_opps_link = {}
        for index, item in enumerate(self._core_populations):
            calc_inf(core_players, core_opps_all, core_opps_core, index, item)
            calc_xref(core_opps_link, index, item, self._link_populations)
        for index, item in enumerate(self._link_populations):
            calc_inf(link_players, link_opps_all, link_opps_link, index, item)
            calc_xref(link_opps_rest, index, item, self._remainder_populations)
            calc_xref(link_opps_core, index, item, self._core_populations)
        for index, item in enumerate(self._remainder_populations):
            calc_inf(rest_players, rest_opps_all, rest_opps_rest, index, item)
            calc_xref(rest_opps_link, index, item, self._link_populations)
        self._core_players = core_players
        self._core_opps_all = core_opps_all
        self._core_opps_core = core_opps_core
        self._core_opps_link = core_opps_link
        self._link_players = link_players
        self._link_opps_all = link_opps_all
        self._link_opps_link = link_opps_link
        self._link_opps_rest = link_opps_rest
        self._link_opps_core = link_opps_core
        self._rest_players = rest_players
        self._rest_opps_all = rest_opps_all
        self._rest_opps_rest = rest_opps_rest
        self._rest_opps_link = rest_opps_link


def mean(nums):
    """Return arithmetic mean of list of numbers."""
    try:
        return sum(nums) / float(len(nums))
    except ZeroDivisionError:
        return None


def median(nums):
    """Return median of a list of numbers."""
    numscopy = sorted(nums)
    size = len(numscopy)
    mid = size // 2
    if (size % 2) == 0:
        return (numscopy[mid] + numscopy[mid - 1]) / 2.0
    return float(numscopy[mid])


def stdev(nums):
    """Return sample standard deviation of a list of numbers."""
    avg = mean(nums)
    try:
        return math.sqrt(sumsq([x - avg for x in nums]) / (len(nums) - 1))
    except ZeroDivisionError:
        return None
    except Exception:
        if avg is None:
            return None
        raise


def sumsq(nums):
    """Return sum of squares of a list of numbers."""
    return sum(x * x for x in nums)
