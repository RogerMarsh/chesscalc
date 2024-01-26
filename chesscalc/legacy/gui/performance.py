# performance.py
# Copyright 2012 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Display chess performance calculation by iteration for selected events."""
import tkinter

from solentware_misc.gui.reports import AppSysReport

from ..core import performances


class Performance:
    """Chess performance calculation report."""

    def __init__(
        self,
        parent,
        title,
        events,
        games,
        players,
        game_opponent,
        opponents,
        names,
        show_report=AppSysReport,
    ):
        """Create widget to display performance calculations for games."""
        super().__init__()
        self.games = games
        self.players = players
        self.game_opponent = game_opponent
        self.opponents = opponents
        if names is None:
            self.names = {}
        else:
            self.names = names
        for key in self.players.keys():
            if key not in self.names:
                self.names[key] = str(key)
        self.performance = None
        self.calculation = None

        self.perfcalc = show_report(
            parent=parent,
            title=title,
            save=(
                "Save",
                "Save Performance Report",
                True,
            ),
            close=(
                "Close",
                "Close Performance Report",
                True,
            ),
            wrap=tkinter.WORD,
            tabstyle="tabular",
        )
        self.perfcalc.append("Events included:\n\n")
        self.perfcalc.append(events)

        self.calculate_performance()

    def calculate_performance(self):
        """Calculate performances by iteration."""
        if self.performance is not None:
            return
        self.performance = performances.Performances()
        self.performance.get_events(
            self.games, self.players, self.game_opponent, self.opponents
        )
        self.performance.find_distinct_populations()
        if self.performance.populations is None:
            self.perfcalc.append(
                "\n\nNo players in selected events",
            )
            return
        if len(self.performance.populations) == 0:
            self.perfcalc.append(
                "\n\nNo players in selected events",
            )
            return
        pops = [len(p) for p in self.performance.populations]
        if len(self.performance.populations) > 1:
            self.perfcalc.append(
                "".join(
                    (
                        "\n\nPlayers in selected events ",
                        "do not form a connected population.\n",
                    )
                )
            )
            self.perfcalc.append(
                "".join(
                    (
                        "\tPlayers in populations are: ",
                        repr(pops),
                        "\n",
                    )
                )
            )
            if (max(pops) * 100) / sum(pops) > 95:
                self.performance.get_largest_population()
                self.performance.find_distinct_populations()
                self.perfcalc.append(
                    "".join(
                        (
                            "\tLargest population is over 95% of total ",
                            "for selected events.\n",
                            "\tCalculation continued using largest ",
                            "population.\n",
                        )
                    )
                )
            else:
                self.perfcalc.append(
                    "".join(
                        (
                            "\tLargest population is less than 95% of total ",
                            "for selected events.\n",
                        )
                    ),
                )
                return
        else:
            self.perfcalc.append(
                "".join(
                    (
                        "\n\nAll players for selected events ",
                        "used in calculation.\n",
                    )
                )
            )
        cscgoo = self.performance.cycle_state_connected_graph_of_opponents()
        if cscgoo:
            self.perfcalc.append(
                "".join(
                    (
                        "\nNo opponent cycles in selected events.",
                        ".\n\nShortest possible is A plays B, B plays C, C ",
                        "plays A: a 3-cycle.\n\nThe workaround is attach a ",
                        "3-cycle using two artifical player names to an ",
                        "existing player who plays games against only one ",
                        "opponent.  The three added games should be draws.",
                    )
                )
            )
            return
        self.perfcalc.append(
            "".join(
                (
                    "\nNumber of players in performance calculation is: ",
                    repr(max(pops)),
                    "\n",
                )
            )
        )

        s_calculation = performances.Calculation(
            self.performance.populations[0],
            self.performance.games,
            self.performance.game_opponent,
            iterations=1000,
        )
        iterations, delta, stable = s_calculation.do_iterations_until_stable(
            cycles=cscgoo
        )
        if not stable:
            self.perfcalc.append(
                "".join(
                    (
                        "\nNo opponent cycles in selected events like: A ",
                        "plays B, B plays C, C plays A.\n\n",
                        "This is a 3-cycle and when present, the usual case, ",
                        "ensures the iteration will converge.",
                        "\n\nAn n-cycle, n>3, exists but this does not ",
                        "ensure the iteration will converge: it depends on ",
                        "the pattern of results of the games in the cycle.  ",
                        "This case seems to be one which does not converge.",
                        "\n\nhe workaround is attach a 3-cycle, using two ",
                        "artifical player names, to an existing player who ",
                        "plays games against only one opponent if possible.  ",
                        "The three added games should be draws.",
                    )
                )
            )
            return
        self.calculation = s_calculation
        self.perfcalc.append(
            "".join(
                (
                    "Iterations used: ",
                    str(iterations),
                    "      Delta: ",
                    str(delta),
                    "\n",
                )
            )
        )

        max_performance = round(
            max(
                p.get_calculated_performance()
                for p in self.calculation.persons.values()
            )
        )
        player_order = sorted(
            [
                (
                    self.names[p][0],
                    -pr.game_count,
                    p,
                    self.names[p][-1],
                    -(
                        round(pr.get_calculated_performance())
                        - max_performance
                    ),
                )
                for p, pr in self.calculation.persons.items()
            ]
        )
        performance_order = sorted(
            [
                (
                    -pr.get_calculated_performance(),
                    -pr.game_count,
                    p,
                    self.names[p][-1],
                    -(
                        round(pr.get_calculated_performance())
                        - max_performance
                    ),
                )
                for p, pr in self.calculation.persons.items()
            ]
        )
        self.perfcalc.append("\n\nPerformances in name order:\n\n")
        output = []
        for item in player_order:
            output.append(
                "".join(
                    (
                        item[3],
                        "\t\t\t",
                        str(item[4]),
                        "\t",
                        "(",
                        str(-item[1]),
                        ")\t\n",
                    )
                )
            )
        self.perfcalc.append("".join(output))
        self.perfcalc.append("\n\nPerformances in performance order:\n\n")
        output = []
        for item in performance_order:
            output.append(
                "".join(
                    (
                        str(item[4]),
                        "\t",
                        "(",
                        str(-item[1]),
                        ")\t\t",
                        item[3],
                        "\n",
                    )
                )
            )
        self.perfcalc.append("".join(output))
        if self.performance.discarded_players is not None:
            discarded_players = sorted(
                [self.names[p] for p in self.performance.discarded_players]
            )
            self.perfcalc.append(
                "\n\nPlayers not included in performance calculation:\n\n"
            )
            self.perfcalc.append("\n".join((n[-1] for n in discarded_players)))
