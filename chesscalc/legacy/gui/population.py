# population.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Display chess player population map analysis."""
import tkinter

from solentware_misc.gui.reports import AppSysReport

from ..core import performances


class Population:
    """Chess population map analysis."""

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
        """Create widget to display population map analysis."""
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
        self.population_maps = None

        self.mapcalc = show_report(
            parent=parent,
            title=title,
            save=(
                "Save",
                "Save Population Report",
                True,
            ),
            close=(
                "Close",
                "Close Population Report",
                True,
            ),
            wrap=tkinter.WORD,
            tabstyle="tabular",
        )
        self.mapcalc.append("Events included:\n\n")
        self.mapcalc.append(events)

        self.calculate_population_map()

    def calculate_population_map(self):
        """Calculate population maps.

        The calculation stops at the point where the population fractures after
        removing players who have played 1, 2, 3, ... opponents in turn.  No
        good reason for not going on till the population is empty, but the
        fracturing algorithm stops at this point.

        """
        if self.performance is not None:
            return

        # Output is buffered for, in practical terms, an infinite improvement
        # in time taken to display answer on OpenBSD.
        output = []

        self.performance = performances.Performances()
        self.performance.get_events(
            self.games, self.players, self.game_opponent, self.opponents
        )
        self.performance.find_distinct_populations()
        if self.performance.populations is None:
            output.append(
                "\n\nNo players in selected events",
            )
            return
        if len(self.performance.populations) == 0:
            output.append(
                "\n\nNo players in selected events",
            )
            return
        pops = [len(p) for p in self.performance.populations]
        if len(self.performance.populations) > 1:
            output.append(
                "".join(
                    (
                        "\n\nPlayers in selected events ",
                        "do not form a connected population.\n",
                    )
                )
            )
            output.append(
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
                output.append(
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
                output.append(
                    "".join(
                        (
                            "\tLargest population is less than 95% of total ",
                            "for selected events.\n",
                        )
                    ),
                )
                return
        else:
            output.append(
                "".join(
                    (
                        "\n\nAll players for selected events ",
                        "used in calculation.\n",
                    )
                )
            )
        if self.performance.is_connected_graph_of_opponents_a_tree():
            output.append(
                "".join(
                    (
                        "\n\nNo opponent cycles in selected events.",
                        "".join(
                            (
                                ".\n\t(shortest possible is A plays B, ",
                                "B plays C, C plays A).\n",
                            )
                        ),
                    )
                )
            )
            return
        output.append(
            "".join(
                (
                    "\nNumber of players in population map analysis is: ",
                    repr(max(pops)),
                    "\n",
                )
            )
        )
        self.performance.find_population_fracture_points()
        population_maps = [
            performances.PopulationMap(
                self.performance, partitioning_edge_count=count
            )
            for count in range(len(self.performance.subpopulations[-1]))
        ]
        for item in population_maps:
            item.rebuild_populations()
        self.population_maps = population_maps
        for index, item in enumerate(population_maps):
            (
                core_players,
                core_opps_all,
                core_opps_core,
                core_opps_link,
                link_players,
                link_opps_all,
                link_opps_link,
                link_opps_rest,
                link_opps_core,
                rest_players,
                rest_opps_all,
                rest_opps_rest,
                rest_opps_link,
            ) = item.population_information
            if len(core_players) == 1:
                msg = "".join(
                    (
                        "\n\n\n",
                        "Each player in the core population played at least ",
                        str(index + 1),
                        " opponents from the whole population.\n",
                        "The number of players in the core population is: ",
                    )
                )
                allmsg = "".join(
                    (
                        "\nThe number of all opponents of players in the ",
                        "core population is: ",
                    )
                )
                coremsg = "".join(
                    (
                        "\nThe number of core opponents of players in the ",
                        "core population is: ",
                    )
                )
            else:
                msg = "".join(
                    (
                        "\n\n\n",
                        "Each player in a core population played at least ",
                        str(index + 1),
                        " opponents from the whole population.\n",
                        "The numbers of players in the core populations are: ",
                    )
                )
                allmsg = "".join(
                    (
                        "\nThe numbers of all opponents of players in the ",
                        "core populations are: ",
                    )
                )
                coremsg = "".join(
                    (
                        "\nThe numbers of core opponents of players in the ",
                        "core populations are: ",
                    )
                )
            output.append(msg)
            rep = [
                "".join(("\n\t", str(k), ": ", str(v)))
                for k, v in sorted(core_players.items())
            ]
            output.append("".join(rep))
            output.append(allmsg)
            rep = [
                "".join(("\n\t", str(k), ": ", str(v)))
                for k, v in sorted(core_opps_all.items())
            ]
            output.append("".join(rep))
            output.append(coremsg)
            rep = [
                "".join(("\n\t", str(k), ": ", str(v)))
                for k, v in sorted(core_opps_core.items())
            ]
            output.append("".join(rep))
            if sum(len(v) for v in core_opps_link.values()) == 0:
                output.append("\nThere are no opponents in link populations.")
            else:
                output.append(
                    "".join(
                        (
                            "\nThe number of opponents of core players in ",
                            "the link populations are: ",
                        )
                    )
                )
                rep = [
                    "".join(
                        (
                            "\n\t",
                            str(k),
                            ":\t{",
                            "".join(
                                [
                                    "".join(("\n\t\t", str(vk), ": ", str(vv)))
                                    for vk, vv in v.items()
                                ]
                            ),
                            "\n\t\t}",
                        )
                    )
                    for k, v in sorted(core_opps_link.items())
                ]
                output.append("".join(rep))
            if len(link_players) == 0:
                continue
            if len(link_players) == 1:
                msg = "".join(
                    (
                        "\nEach player in the link population played at most ",
                        str(index),
                        " opponents from the whole population, including at ",
                        "least one opponent from a core population.\n",
                        "The number of players in the link population is: ",
                    )
                )
                allmsg = "".join(
                    (
                        "\nThe number of all opponents of players in the ",
                        "link population is: ",
                    )
                )
                linkmsg = "".join(
                    (
                        "\nThe number of link opponents of players in the ",
                        "link population is: ",
                    )
                )
            else:
                msg = "".join(
                    (
                        "\nEach player in a link population played at most ",
                        str(index),
                        " opponents from the whole population, including at ",
                        "least one opponent from a core population.\n",
                        "The numbers of players in the link populations are: ",
                    )
                )
                allmsg = "".join(
                    (
                        "\nThe numbers of all opponents of players in the ",
                        "link populations are: ",
                    )
                )
                linkmsg = "".join(
                    (
                        "\nThe numbers of link opponents of players in the ",
                        "link populations are: ",
                    )
                )
            output.append(msg)
            rep = [
                "".join(("\n\t", str(k), ": ", str(v)))
                for k, v in sorted(link_players.items())
            ]
            output.append("".join(rep))
            output.append(allmsg)
            rep = [
                "".join(("\n\t", str(k), ": ", str(v)))
                for k, v in sorted(link_opps_all.items())
            ]
            output.append("".join(rep))
            rep = [
                "".join(("\n\t", str(k), ": ", str(v)))
                for k, v in sorted(link_opps_link.items())
            ]
            if len(rep):
                output.append(linkmsg)
                output.append("".join(rep))
            else:
                output.append(
                    "".join(
                        (
                            "\nNo players in link populations played ",
                            "opponents in their link population.",
                        )
                    )
                )
            if sum(len(v) for v in link_opps_rest.values()) == 0:
                output.append(
                    "\nThere are no opponents in remainder populations."
                )
            else:
                output.append(
                    "".join(
                        (
                            "\nThe number of opponents of link players in ",
                            "the remainder populations are: ",
                        )
                    )
                )
                rep = [
                    "".join(
                        (
                            "\n\t",
                            str(k),
                            ":\t{",
                            "".join(
                                [
                                    "".join(("\n\t\t", str(vk), ": ", str(vv)))
                                    for vk, vv in v.items()
                                ]
                            ),
                            "\n\t\t}",
                        )
                    )
                    for k, v in sorted(link_opps_rest.items())
                    if len(v)
                ]
                output.append("".join(rep))
            # start link_opps_core
            # This section should give same figures as 'core_opps_link'
            # Remove it?
            output.append(
                "".join(
                    (
                        "\nThe number of opponents of link players in the ",
                        "core populations are: ",
                    )
                )
            )
            rep = [
                "".join(
                    (
                        "\n\t",
                        str(k),
                        ":\t{",
                        "".join(
                            [
                                "".join(("\n\t\t", str(vk), ": ", str(vv)))
                                for vk, vv in v.items()
                            ]
                        ),
                        "\n\t\t}",
                    )
                )
                for k, v in sorted(link_opps_core.items())
            ]
            output.append("".join(rep))
            # end link_opps_core
            if len(rest_players) == 0:
                continue
            if len(rest_players) == 1:
                msg = "".join(
                    (
                        "\nEach player in the remainder population played at ",
                        "most ",
                        str(index),
                        " opponents from the whole population, including at ",
                        "least one opponent from a link population but no ",
                        "opponents from a core population.\n",
                        "The number of players in the remainder population ",
                        "is: ",
                    )
                )
                allmsg = "".join(
                    (
                        "\nThe number of all opponents of players in the ",
                        "remainder population is: ",
                    )
                )
                restmsg = "".join(
                    (
                        "\nThe number of remainder opponents of players in ",
                        "the remainder population is: ",
                    )
                )
            else:
                msg = "".join(
                    (
                        "\nEach player in a remainder population played at ",
                        "most ",
                        str(index),
                        " opponents from the whole population, including at ",
                        "least one opponent from a link population but no ",
                        "opponents from a core population.\nThe numbers of ",
                        "players in the remainder populations are: ",
                    )
                )
                allmsg = "".join(
                    (
                        "\nThe numbers of all opponents of players in the ",
                        "remainder populations are: ",
                    )
                )
                restmsg = "".join(
                    (
                        "\nThe numbers of remainder opponents of players in ",
                        "the remainder populations are: ",
                    )
                )
            output.append(msg)
            rep = [
                "".join(("\n\t", str(k), ": ", str(v)))
                for k, v in sorted(rest_players.items())
            ]
            output.append("".join(rep))
            output.append(allmsg)
            rep = [
                "".join(("\n\t", str(k), ": ", str(v)))
                for k, v in sorted(rest_opps_all.items())
            ]
            output.append("".join(rep))
            rep = [
                "".join(("\n\t", str(k), ": ", str(v)))
                for k, v in sorted(rest_opps_rest.items())
            ]
            if len(rep):
                output.append(restmsg)
                output.append("".join(rep))
            else:
                output.append(
                    "".join(
                        (
                            "\nNo players in remainder populations played ",
                            "oppenents in their remainder population.",
                        )
                    )
                )
            # start rest_opps_link
            # This section should give same figures as 'link_opps_rest'
            # Remove it?
            output.append(
                "".join(
                    (
                        "\nThe number of opponents of remainder players in ",
                        "the link populations are: ",
                    )
                )
            )
            rep = [
                "".join(
                    (
                        "\n\t",
                        str(k),
                        ":\t{",
                        "".join(
                            [
                                "".join(("\n\t\t", str(vk), ": ", str(vv)))
                                for vk, vv in v.items()
                            ]
                        ),
                        "\n\t\t}",
                    )
                )
                for k, v in sorted(rest_opps_link.items())
            ]
            output.append("".join(rep))
            # end rest_opps_link
        self.mapcalc.append("".join(output))
