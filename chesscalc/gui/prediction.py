# prediction.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Display chess performance predictions by season for selected events.

"""
import tkinter

from solentware_misc.gui.reports import show_report

from ..core import performances


class Prediction(object):
    """Chess performance calculation report.
    
    """

    def __init__(
        self,
        parent,
        title,
        events,
        seasons,
        games,
        players,
        game_opponent,
        opponents,
        names):
        """Create widget to display performance calculations for games"""
        super(Prediction, self).__init__()
        self.seasons = seasons
        self.games = games
        self.players = players
        self.game_opponent = game_opponent
        self.opponents = opponents
        if names is None:
            self.names = dict()
        else:
            self.names = names
        for p in self.players.keys():
            if p not in self.names:
                self.names[p] = str(p)
        self.predictions = None
        self.calculations = None

        self.perfcalc = show_report(
            parent,
            title,
            save=(
                'Save',
                'Save Prediction Report',
                True,
                ),
            close=(
                'Close',
                'Close Prediction Report',
                True,
                ),
            wrap=tkinter.WORD,
            tabstyle='tabular',
            )
        self.perfcalc.append('Events included:\n\n')
        self.perfcalc.append(events)
        
        self.calculate_prediction()

    def calculate_prediction(self):
        if self.predictions is not None:
            return

        # Output is buffered for, in practical terms, an infinite improvement
        # in time taken to display answer on OpenBSD.
        pc = []

        self.predictions = {}
        self.calculations = {}
        s_seasons = self.seasons
        s_games = self.games
        s_players = self.players
        s_game_opponent = self.game_opponent
        s_opponents = self.opponents
        s_names = self.names
        for s in sorted(self.seasons):
            sv = self.seasons[s]
            season_start = '-'.join((s.split('-')[0], '07', '01'))
            games = {}
            game_opponent = {}
            players = {}
            game_opponent = {}
            opponents = {}
            names = {}
            for g in sv:
                games[g] = s_games[g]
                game_opponent[g] = s_game_opponent[g]
                for p in games[g]:
                    players.setdefault(p, set()).add(g)
            for p in players:
                opponents[p] = {o for o in s_opponents[p] if o in players}
                names[p] = s_names[p]
            # Now do the base performance calculation for each season
            s_performance = performances.Performances()
            s_performance.get_events(
                games,
                players,
                game_opponent,
                opponents)
            s_performance.find_distinct_populations()
            if s_performance.populations is None:
                pc.append(
                    ''.join(
                        ('\n\nNo players in season starting ',
                         season_start,
                         '.',
                         )),
                    )
                continue
            if len(s_performance.populations) == 0:
                pc.append(
                    ''.join(
                        ('\n\nNo players in season starting ',
                         season_start,
                         '.',
                         )),
                    )
                continue
            pops = [len(p) for p in s_performance.populations]
            if len(s_performance.populations) > 1:
                pc.append(
                    ''.join(
                        ('\n\nPlayers do not form a connected population in ',
                         'season starting ',
                         season_start,
                         '.\n',
                         )))
                pc.append(
                    ''.join(
                        ('\tPlayers in populations are: ',
                         repr(pops),
                         '\n',
                         )))
                if (max(pops) * 100) / sum(pops) > 95:
                    s_performance.get_largest_population()
                    s_performance.find_distinct_populations()
                    pc.append(
                        ''.join(
                            ('\tLargest population is over 95% of total ',
                             'for season starting ',
                             season_start,
                             '.\n\tCalculation continued using largest ',
                             'population.\n',
                             )))
                else:
                    pc.append(
                        ''.join(
                            ('\tLargest population is less than 95% of total ',
                             'for season starting ',
                             season_start,
                             '.\n',
                             )),
                        )
                    continue
            else:
                pc.append(
                    ''.join(
                        ('\n\nAll players used in calculation for season ',
                         'starting ',
                         season_start,
                         '.\n',
                         )))
            pc.append(
                ''.join(
                    ('Number of players is: ',
                     repr(max(pops)),
                     '\n',
                     )))
            pc.append(
                ''.join(
                    ('Number of half-games is: ',
                     repr(sum([len(players[p])
                               for p in s_performance.populations[0]])),
                     '\n',
                     )))
            cscgoo = s_performance.cycle_state_connected_graph_of_opponents()
            if cscgoo is True:
                pc.append(
                    ''.join(
                        ('\n\nNo opponent cycles in season starting ',
                         season_start,
                         '.\n\nShortest possible is A plays B, B plays C, C ',
                         'plays A: a 3-cycle.\n\nThe workaround is attach a ',
                         '3-cycle using two artifical player names to an ',
                         'existing player who plays games against only one ',
                         'opponent.  The three added games should be draws.',
                         )))
                continue

            s_calculation = performances.Calculation(
                s_performance.populations[0],
                s_performance.games,
                s_performance.game_opponent,
                iterations=1000)
            (iterations,
             delta,
             stable) = s_calculation.do_iterations_until_stable(cycles=cscgoo)
            if not stable:
                pc.append(
                    ''.join(
                        ('\n\nNo opponent cycles in season ',
                         season_start,
                         ' like: A plays B, B plays C, C plays A.\n\n',
                         'This is a 3-cycle and when present, the usual case, ',
                         'ensures the iteration will converge.',
                         '\n\nAn n-cycle, n>3, exists but this does not ',
                         'ensure the iteration will converge: it depends on ',
                         'the pattern of results of the games in the cycle.  ',
                         'This case seems to be one which does not converge.',
                         '\n\nThe workaround is attach a 3-cycle, using two ',
                         'artifical player names, to an existing player who ',
                         'plays games against only one opponent if possible.  ',
                         'The three added games should be draws.',
                         )))
                continue
            self.calculations[s] = s_calculation
            pc.append(''.join(
                ('Iterations used: ',
                 str(iterations),
                 '      Delta: ',
                 str(delta),
                 '\n',
                 )))

        for ref in sorted(self.calculations):
            ref_start = '-'.join((ref.split('-')[0], '07', '01'))
            self.predictions[ref] = {}
            self.predictions[ref][ref] = performances.Distribution(
                self.calculations[ref], self.calculations[ref])
            pc.append(''.join(
                ('\nSeason starting ',
                 ref_start,
                 ' used to partition results.\nPlayers: ',
                 str(len(self.predictions[ref][ref].players)),
                 '      games: ',
                 str(len(self.predictions[ref][ref].games)),
                 '\n',
                 )))
            for target in sorted(self.calculations):
                if ref == target:
                    continue
                target_start = '-'.join((target.split('-')[0], '07', '01'))
                self.predictions[ref][target] = performances.Distribution(
                    self.calculations[ref], self.calculations[target])
                pc.append(''.join(
                    ('Players: ',
                     str(len(self.predictions[ref][target].players)),
                     '      games: ',
                     str(len(self.predictions[ref][target].games)),
                     '  comparable in season starting ',
                     target_start,
                     '\n',
                     )))
        self.perfcalc.append(''.join(pc))

        for bs in (5, 1, 10):
            self.report_prediction(bs)

    def report_prediction(self, bucket_size):

        # Output is buffered for, in practical terms, an infinite improvement
        # in time taken to display answer on OpenBSD.
        pc = []

        pc.append(''.join(
            ('\n\nReports with buckets of width ',
             str(bucket_size),
             ' for performance difference between players of a game.\n\n',
             )))
        for ref in sorted(self.predictions):
            ref_start = '-'.join((ref.split('-')[0], '07', '01'))
            self.predictions[ref][ref].calculate_distribution(bucket_size)
            distribution = self.predictions[ref][ref].distributions[bucket_size]
            pc.append(''.join(
                ('\nDistribution calculated from results for season starting ',
                 ref_start,
                 '\n',
                 )))
            for bucket in sorted(distribution):
                b = distribution[bucket]
                percent = round(
                    ((b.wins * 2 + b.draws) * 50) /
                    (b.wins + b.draws + b.losses), 1)
                pc.append(''.join(
                    ('< ',
                     str(b.base + b.width),
                     '\t\t+',
                     str(b.wins),
                     '\t=',
                     str(b.draws),
                     '\t-',
                     str(b.losses),
                     '\t\t',
                     str(percent),
                     '\n',
                     )))

        for target in sorted(self.predictions):
            target_start = '-'.join((target.split('-')[0], '07', '01'))
            for ref in sorted(self.predictions):
                if ref == target:
                    continue
                ref_start = '-'.join((ref.split('-')[0], '07', '01'))
                self.predictions[ref][target].calculate_distribution(
                    bucket_size)
                distribution = self.predictions[ref][target].distributions[
                    bucket_size]
                pc.append(''.join(
                    ('\n',
                     target_start,
                     ' season results partitioned by performances in season ',
                     ref_start,
                     '\n',
                     )))
                for bucket in sorted(distribution):
                    b = distribution[bucket]
                    percent = round(
                        ((b.wins * 2 + b.draws) * 50) /
                        (b.wins + b.draws + b.losses), 1)
                    pc.append(''.join(
                        ('< ',
                         str(b.base + b.width),
                         '\t\t+',
                         str(b.wins),
                         '\t=',
                         str(b.draws),
                         '\t-',
                         str(b.losses),
                         '\t\t',
                         str(percent),
                         '\n',
                         )))
        self.perfcalc.append(''.join(pc))
