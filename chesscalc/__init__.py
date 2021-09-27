# __init__.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Calculate player's performances on a set of games.

Performances are calculated by iteration where each player starts with 0 as
their performance.  The scale used is +50 for a win, -50 for a loss, and 0 for
a draw, relative to the opponents performance.  English Chess Federation (ECF)
grades have the same scale.

The performances are not grades because the results of calculations in previous
runs are not used in this calculation.

"""
APPLICATION_NAME = "ChessPerfCalc"
ERROR_LOG = "ErrorLog"
