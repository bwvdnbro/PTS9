#!/usr/bin/env python
# -*- coding: utf8 -*-
# *****************************************************************
# **       PTS -- Python Toolkit for working with SKIRT          **
# **       © Astronomical Observatory, Ghent University          **
# *****************************************************************

## \package pts.test.functional Contains the SkirtTestSuite class for performing a suite of SKIRT test cases
#
# An instance of the SkirtTestSuite class in this module represents a suite of functional SKIRT test cases, stored as
# a nested structure of files and directories according to a specific layout, and provides facilities to
# perform the tests, verify the results, and prepare a summary test report.

# -----------------------------------------------------------------

import logging
import pts.simulation as sm
import pts.utils as ut

# -----------------------------------------------------------------

## An instance of the SkirtTestSuite class represents a suite of SKIRT test cases, stored as
# a nested structure of files and directories according to a specific layout, and provides facilities to
# perform the tests, verify the results, and prepare a summary test report.
#
# A test suite consists of a set of independent test cases (i.e. test cases can be executed in arbitrary order)
#
# Each test case in a test suite is defined by a collection of files and directories as follows:
#  - a directory with arbitrary name containing all test case files and directories, called the "case directory";
#    a test suite is named after this directory
#  - immediately inside the case directory there is:
#    - exactly one \em ski file with an arbitrary name (with the \c .ski filename extension) specifying the simulation
#      to be performed for the test case
#    - a directory named \c in containing the input files for the simulation, if any
#    - a directory named \c ref containing the reference files for the test, i.e. a copy of the output files
#      generated by a correct simulation run
#    - a directory named \c out to receive the actual output files when the test is performed; the contents
#      of this directory are automatically removed and recreated when running the test case
#    - everything else is ignored, as long as there are no additional files with a \c .ski filename extension
#
# A test suite is defined by a collection of files and directories as follows:
#  - a directory directly or indirectly containing all test cases, called the "suite directory";
#    a test suite is named after this directory
#  - each ski file directly or indirectly contained in the suite directory defines a test case that
#    must adhere to the description above (no other ski files in the same directory, special directories
#    next to the \em ski file, etc.)
#
# For example, a test suite may be structured with nested sub-suites as follows (where each \c CaseN directory
# contains a ski file plus \c ref, \c in, and \c out directories):
#
# \verbatim
# SKIRT Tests
#   SPH simulations
#       Case1
#       Case2
#   Geometries
#     Radial
#         Case1
#         Case2
#     Cylindrical
#         Case1
#         Case2
#         Case3
#     Full 3D
#         Case1
#         Case2
#   Instruments
# \endverbatim
#
# It is also allowed to nest test cases inside another test case, but this is not recommended.
#
class SkirtTestSuite:

    ## The first argument accepted by the constructor indicates the selection of functional tests to be performed:
    #  - "." (a single period): perform all test cases in the standard suite.
    #  - "testcase" (the name of a test case directory): perform all test cases with that name.
    #  - "subsuite" (the name of an intermediate directory in the hierarchy): perform the test cases in all sub-suites
    #    with that name.
    #  - "parentsubsuite/testcase" or "parentsubsuite/subsuite": perform the indicated test case(s) or sub-suite(s)
    #    that reside immediately inside the indicated parent sub-suite; this can disambiguate items with the same name.
    #
    # In addition, the constructor accepts the following optional arguments:
    #  - suitePath: the path of the directory containing the complete functional test suite.
    #  - skirtPath: this optional argument specifies the path to the skirt executable.
    #
    # If specified, these paths are interpreted as described for the pts.utils.absPath() function. If omitted, the
    # default paths are pts.utils.projectParentPath()/"Functional9" and pts.utils.skirtPath(), respectively.
    #
    def __init__(self, subSuite=".", *, suitePath=None, skirtPath=None):

        # set the top-level suite path
        self._suitePath = ut.absPath(suitePath) if suitePath is not None else ut.projectParentPath()/"Functional9"

        # find all matching sub-suite paths
        if subSuite is None or subSuite == "" or "." in subSuite:
            subSuitePaths = [ self._suitePath ]
        else:
            subSuitePaths = self._suitePath.rglob(subSuite)

        # find all valid test cases in any of the sub-suite paths and remember the paths to the corresponding ski files
        skiPathSet = set()
        for subSuitePath in subSuitePaths:
            for skiPath in subSuitePath.rglob("*.ski"):
                if len(list(skiPath.parent.glob("*.ski"))) == 1:
                    skiPathSet.add(skiPath)
        self._skiPaths = sorted(skiPathSet)

        # abort if there are no valid test cases
        if len(self._skiPaths) == 0:
            raise ut.UserError("No valid test cases found for sub-suite specification: '{}'".format(subSuite))

        # create a SKIRT execution context
        self._skirt = sm.Skirt(skirtPath)

    ## This function performs all tests in the test suite, verifies the results, and prepares a summary test report.
    def perform(self):
        # inform the user of the fact that the tests are being initiated
        logging.info("Performing {} functional test case(s)".format(len(self._skiPaths)))
        #logging.info("Using " + self._skirt.version() + " at " + self._skirt.path())


# -----------------------------------------------------------------