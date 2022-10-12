# calculator.py
# Copyright 2012 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Display chess performance calculation by iteration for file of games."""

import tkinter
import tkinter.ttk
import tkinter.messagebox
import tkinter.filedialog
import re

from solentware_misc.gui.bindings import Bindings

from ..core import performances
from . import help_

GAME_RE_STR = r"\s*(.*?)\s+(1-0|draw|0-1)\s+(.*?)\s*$"
re_game = re.compile(GAME_RE_STR)
SCORE = {
    "1-0": (1, -1),
    "draw": (0, 0),
    "0-1": (-1, 1),
}


class Calculator(Bindings):
    """Base class for reports and dialogues."""

    def __init__(self):
        """Create widget to display performance calculations for games."""
        super().__init__()
        self.filename = None
        self.games = None
        self.players = None
        self.game_opponent = None
        self.opponents = None
        self.names = None
        self.performance = None
        self.fixed_performance = None
        self.widget = tkinter.Tk()
        self.widget.wm_title("Performance Calculation")
        sbf = tkinter.ttk.Frame(master=self.widget)
        self.sbiter = tkinter.ttk.Spinbox(
            master=sbf, from_=10, to=1000, increment=10
        )
        self.sbiter.set(10)
        self.menubar = tkinter.Menu(master=self.widget)

        def close_display():
            title = "Quit"
            if tkinter.messagebox.askokcancel(
                master=self.widget,
                message="Please confirm Quit action",
                title="Quit display performance calculation",
            ):
                self.widget.winfo_toplevel().destroy()

        def help_about():
            help_.help_about_calculator(self.widget)

        def help_notes():
            help_.help_notes_calculator(self.widget)

        self.menubar.add_command(
            label="Open",
            underline=0,
            command=self.try_command(
                self.get_games_from_text_file, self.menubar
            ),
        )
        self.menubar.add_command(
            label="Quit",
            underline=0,
            command=self.try_command(close_display, self.menubar),
        )
        menuhelp = tkinter.Menu(
            self.menubar, cnf=dict(name="help_", tearoff=False))
        self.menubar.add_cascade(label="Help", menu=menuhelp, underline=0)
        menuhelp.add_command(
            label="Notes",
            underline=0,
            command=self.try_command(help_notes, menuhelp),
        )
        menuhelp.add_command(
            label="About",
            underline=0,
            command=self.try_command(help_about, menuhelp),
        )
        self.widget.configure(menu=self.menubar)
        tkinter.ttk.Label(master=sbf, text="Iterations ").pack(side=tkinter.LEFT)
        self.sbiter.pack(side=tkinter.LEFT)
        sbf.pack(fill=tkinter.X)
        pw = tkinter.ttk.PanedWindow(
            master=self.widget,
            orient=tkinter.VERTICAL,
        )
        pwgames = tkinter.ttk.PanedWindow(
            master=pw, orient=tkinter.VERTICAL
        )
        ef = tkinter.ttk.Frame(master=pwgames)
        self.pcgames = tkinter.Text(
            master=ef, cnf=dict(wrap=tkinter.WORD, tabstyle="tabular")
        )
        scrollbar = tkinter.Scrollbar(
            master=ef, orient=tkinter.VERTICAL, command=self.pcgames.yview
        )
        self.pcgames.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.pcgames.pack(
            side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE
        )
        pwgames.add(ef)
        pwcalc = tkinter.ttk.PanedWindow(
            master=pw, orient=tkinter.VERTICAL
        )
        ef = tkinter.ttk.Frame(master=pwcalc)
        self.report = tkinter.Text(
            master=ef, cnf=dict(wrap=tkinter.WORD, tabstyle="tabular")
        )
        scrollbar = tkinter.ttk.Scrollbar(
            master=ef, orient=tkinter.VERTICAL, command=self.report.yview
        )
        self.report.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.report.pack(
            side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE
        )
        pwcalc.add(ef)
        pw.add(pwgames)
        pw.add(pwcalc)
        pw.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=tkinter.TRUE)

    def calculate_performance(self):
        """Calculate performances for connected population by iteration."""
        if self.filename is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="".join(
                    (
                        "No games input from file for processing.\n\n",
                        "Please open a file to get games to process.",
                    )
                ),
                title="Calculate Performance",
            )
            return
        if self.performance is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="".join(
                    (
                        "Games have not been divided into populations.\n\n",
                        "Please use Find Populations to process games first.",
                    )
                ),
                title="Calculate Performance",
            )
            return
        iteration_count = self.sbiter.get()
        if not iteration_count.isdigit():
            tkinter.messagebox.showinfo(
                message="".join(
                    (
                        "Number of iterations must be a number\n\n",
                        str(iteration_count),
                        " is not allowed.",
                    )
                ),
                title="Calculate Performance",
            )
            return
        self.menubar.delete(1)
        self.fixed_performance = []
        if len(self.performance.subpopulations):
            self.report.insert(tkinter.END, "\n")
        for eigc, igc in enumerate(self.performance.subpopulations):
            for epops, pops in enumerate(igc):
                if len(pops) > 1:
                    self.report.insert(
                        tkinter.END,
                        "".join(
                            (
                                "The following performance calculations ",
                                "are for the subpopulations generated when ",
                                "the first fracture occured.",
                            )
                        ),
                    )
                elif len(pops) == 0:
                    self.report.insert(
                        tkinter.END,
                        "".join(
                            (
                                "The initial population has been reduced to ",
                                "nothing without fracturing.",
                            )
                        ),
                    )
                    break
                if len(self.performance.removed[eigc][epops]) == 0:
                    self.report.insert(
                        tkinter.END,
                        "".join(
                            (
                                "No players in the initial population played ",
                                str(epops + 1),
                                " opponents (some players may have played ",
                                str(epops + 1),
                                " games) so no players will be removed from ",
                                "the population on this cycle and the ",
                                "performance calculation is not done.\n\n",
                            )
                        ),
                    )
                    continue
                for esp, sp in enumerate(pops):
                    if len(sp) == 0:
                        self.report.insert(
                            tkinter.END,
                            "Calculation not done for empty population.\n\n",
                        )
                        continue
                    elif len(sp) == 1:
                        self.report.insert(
                            tkinter.END,
                            "".join(
                                (
                                    "Calculation not done for population ",
                                    "containing one player.\n\n",
                                )
                            ),
                        )
                        continue
                    self.report.insert(
                        tkinter.END,
                        "".join(
                            (
                                "The following performance calculation ",
                                "excludes players who played less than ",
                                str(epops + 1),
                                " opponents.\n\n",
                            )
                        ),
                    )
                    calc = performances.Calculation(
                        sp,
                        self.performance.games,
                        self.performance.game_opponent,
                        iterations=int(iteration_count),
                    )
                    calc.do_iterations()
                    self.fixed_performance.append((epops, dict(), dict()))
                    fpc = self.fixed_performance[-1][-1]
                    fpg = self.fixed_performance[-1][-2]
                    rlines = []
                    for p, pr in calc.persons.items():
                        fpc[p] = pr.get_calculated_performance()
                        fpg[p] = [str(int(round(pr.get_grade())))]
                        if pr.is_performance_stable(1e-12):
                            cps = str(pr.get_calculated_performance())
                        else:
                            cps = "\t\t".join(([str(i) for i in pr.iteration]))
                        if p != self.names[p]:
                            pid = str(p).join(("(", ")\t"))
                        else:
                            pid = ""
                        rlines.append(
                            (
                                self.names[p],
                                "".join(
                                    (
                                        pid,
                                        self.names[p],
                                        "\t\t\t",
                                        str(pr.game_count),
                                        "\t",
                                        str(int(round(pr.get_grade()))),
                                        "\t",
                                        cps,
                                    )
                                ),
                            )
                        )
                    rlines.sort()
                    report_lines = []
                    for s, v in rlines:
                        report_lines.append(v)
                    report_lines.append("\n")
                    statistics = calc.get_statistics()
                    for s in sorted(statistics):
                        report_lines.append(
                            "\t\t\t\t\t".join((s, str(statistics[s])))
                        )
                    report_lines.append("\n\n")
                    self.report.insert(tkinter.END, "\n".join(report_lines))
        if len(self.performance.subpopulations[0][0]) != 1:
            return
        for cfpc, fpg, fpc in self.fixed_performance[1:]:
            calc = performances.Calculation(
                self.performance.subpopulations[0][0][0],
                self.performance.games,
                self.performance.game_opponent,
                iterations=int(iteration_count),
                initialperformance=fpc,
            )
            calc.do_iterations()
            rlines = []
            for p, pr in calc.persons.items():
                if p in fpg:
                    fpg[p].append(str(int(round(pr.get_grade()))))
                else:
                    fpg[p] = ["", str(int(round(pr.get_grade())))]
                if pr.is_performance_stable(1e-12):
                    cps = str(pr.get_calculated_performance())
                else:
                    cps = "\t\t".join(([str(i) for i in pr.iteration]))
                if p != self.names[p]:
                    pid = str(p).join(("(", ")\t"))
                else:
                    pid = ""
                rlines.append(
                    (
                        self.names[p],
                        "".join(
                            (
                                pid,
                                self.names[p],
                                "\t\t\t",
                                str(pr.game_count),
                                "\t",
                                str(int(round(pr.get_grade()))),
                                "\t",
                                cps,
                            )
                        ),
                    )
                )
            rlines.sort()
            report_lines = []
            report_lines.append(
                "".join(
                    (
                        "\n\n\nThe following performance calculation ",
                        "includes all players but the performances ",
                        "calculated earlier by ignoring all players with ",
                        "less than ",
                        str(cfpc + 1),
                        " opponents are used as fixed values for this ",
                        "calculation.",
                        "\n",
                    )
                )
            )
            for s, v in rlines:
                report_lines.append(v)
            report_lines.append("\n")
            statistics = calc.get_statistics()
            for s in sorted(statistics):
                report_lines.append("\t\t\t\t\t".join((s, str(statistics[s]))))
            self.report.insert(tkinter.END, "\n".join(report_lines))
        report_lines = []
        report_lines.append(
            "".join(
                (
                    "\n\n\n\nThe performances calculated for each player are ",
                    "listed in ascending order of number of opponents for ",
                    "ignoring a player to derive a population.  The first ",
                    "line for each player gives the calculated performance ",
                    "with all players included and the second gives the ",
                    "performance if the player was not excluded for ",
                    "playing too few opponents.",
                    "\n",
                )
            )
        )
        fpg = [fp[1] for fp in self.fixed_performance]
        for p in fpg[0]:
            fpg[0][p].append(fpg[0][p][0])
        for p in sorted(self.fixed_performance[0][1]):
            report_lines.append(
                "".join(
                    (
                        str(p),
                        "\t\t\t",
                        "\t".join([pg[p][1] for pg in fpg]),
                    )
                )
            )
            report_lines.append(
                "".join(
                    (
                        "\t\t\t",
                        "\t".join([pg[p][0] for pg in fpg]),
                        "\n",
                    )
                )
            )
        self.report.insert(tkinter.END, "\n".join(report_lines))

    def find_populations(self):
        """Find distinct populations created by removing games one by one."""
        if self.filename is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="".join(
                    (
                        "No games input from file for processing.\n\n",
                        "Please open a file to get games to process.",
                    )
                ),
                title="Find Populations",
            )
            return
        if self.performance is not None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="".join(
                    (
                        "Games input from file have already been processed.",
                        "\n\n",
                        "Nothing done.",
                    )
                ),
                title="Find Populations",
            )
            return
        self.performance = performances.Performances()
        self.performance.get_events(
            self.games, self.players, self.game_opponent, self.opponents
        )
        self.performance.find_distinct_populations()
        self.performance.find_population_fracture_points()
        lines = []
        if len(self.performance.subpopulations[-1][-1]) > 1:
            lines.append(
                "".join(
                    (
                        "The population fractures into ",
                        str(len(self.performance.subpopulations[-1][-1])),
                        " sub-populations when players who played less than ",
                        str(len(self.performance.subpopulations[-1]) - 1),
                        " opponents are ignored.\n",
                    )
                )
            )
        else:
            lines.append(
                "".join(
                    (
                        "The population does not fracture into ",
                        "sub-populations when players are ignored in order ",
                        "by ascending number of opponents played.  Maximum ",
                        "opponents is ",
                        str(len(self.performance.subpopulations[-1]) - 1),
                        ".\n",
                    )
                )
            )
        self.report.insert(tkinter.END, "\n".join(lines))
        self.menubar.entryconfigure(
            1, label="Performance", command=self.calculate_performance
        )

    def get_games_from_text_file(self):
        """Get games from a file with one game per line."""
        filename = tkinter.filedialog.askopenfilename(
            parent=self.pcgames,
            title="Open file",
            # defaultextension='.txt',
            filetypes=(
                ("All files", "*"),
                ("Text", "*.txt *.TXT"),
            ),
        )
        if filename:
            games = dict()
            players = dict()
            game_opponent = dict()
            opponents = dict()
            names = dict()
            lines = []
            inp = open(filename, mode="r", encoding="utf-8")
            try:
                for line in inp:
                    gn = len(games)
                    g = re_game.match(line)
                    if g is None:
                        continue
                    g = [" ".join(e.split()) for e in g.groups()]
                    lines.append("\t\t\t".join(g))
                    for a in (g[0], g[2]):
                        if a not in players:
                            players[a] = {gn}
                            names[a] = a
                        else:
                            players[a].add(gn)
                        if a not in opponents:
                            opponents[a] = set()
                    game_opponent[gn] = {g[0]: g[2], g[2]: g[0]}
                    opponents[g[0]].add(g[2])
                    opponents[g[2]].add(g[0])
                    result = dict()
                    result[g[0]] = SCORE[g[1]][0]
                    result[g[2]] = SCORE[g[1]][1]
                    games[gn] = result
                else:
                    self.pcgames.delete("1.0", tkinter.END)
                    self.pcgames.insert(tkinter.END, "\n".join(lines))
                    self.filename = filename
                    self.games = games
                    self.players = players
                    self.game_opponent = game_opponent
                    self.opponents = opponents
                    self.names = names
                    self.performance = None
                    self.pcgames.winfo_toplevel().wm_title(filename)
                    self.menubar.entryconfigure(
                        1,
                        label="Find populations",
                        command=self.find_populations,
                    )
            finally:
                inp.close()
