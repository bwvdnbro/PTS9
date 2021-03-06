#!/usr/bin/env python
# -*- coding: utf8 -*-
# *****************************************************************
# **       PTS -- Python Toolkit for working with SKIRT          **
# **       © Astronomical Observatory, Ghent University          **
# *****************************************************************

## \package pts.visual.do.plot_density_cuts Plot planar cuts through the medium density in one or more SKIRT simulations
#
# This script creates plots of media density cuts generated by the DefaultMediaDensityCutsProbe or
# PlanarMediaDensityCutsProbe in a SKIRT simulation, allowing a visual comparison between the theoretical
# and spatially gridded medium density distribution.
#
# If the simulation does not include any DefaultMediaDensityCutsProbe or PlanarMediaDensityCutsProbe instances,
# the script does nothing.
#
# The script takes the following arguments:
#  - \em simDirPath (positional string argument): the path to the SKIRT simulation output directory,
#                                                 or "." for the current directory
#  - \em prefix (string): the prefix of the simulation to handle; by default handles all simulations in the directory
#  - \em dex (float): if specified, the number of decades to be included in the density range (color bar); default is 5
#
# In all cases, the plot file is placed next to the simulation output file(s) being handled. The filename includes
# the simulation prefix, the probe name, and the medium and cut indicators, and has the ".pdf" filename extension.
#

# -----------------------------------------------------------------

def do( simDirPath : (str, "SKIRT simulation output directory"),
        prefix : (str,"SKIRT simulation prefix") = "",
        dex : (float,"number of decades to be included in the density range (color bar)") = 5,
        ) -> "plot the planar cuts through the medium density in one or more SKIRT simulations":

    import pts.simulation as sm
    import pts.visual as vis

    for sim in sm.createSimulations(simDirPath, prefix if len(prefix) > 0 else None):
        vis.plotMediaDensityCuts(sim, decades=dex)

# ----------------------------------------------------------------------
