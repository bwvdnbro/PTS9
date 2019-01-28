#!/usr/bin/env python
# -*- coding: utf8 -*-
# *****************************************************************
# **       PTS -- Python Toolkit for working with SKIRT          **
# **       © Astronomical Observatory, Ghent University          **
# *****************************************************************

## \package pts.admin.do.create_backup Create backup archives for the SKIRT/PTS parent project
#
# This script creates backup archives (ZIP files) for the SKIRT/PTS parent project as directed by
# the contents of a simple command file residing in the hierarchy of the project directory.
# The script assumes a directory structure similar to the following example:
#
#     <project-parent-directory>
#         Backup
#             create_backup.txt
#             Backup--2019-01-28--10-09-27
#         Benchmark9
#         Functional9
#         PTS9
#             pts
#             run
#         Resources9
#         SKIRT9
#             git
#             run
#
# In this example, the code for this script resides in the \c .../PTS9/pts/admin/do directory.
# The file \c .../Backup/create_backup.txt contains backup creation instructions interpreted by this script.
# The ZIP archives generated by the script are placed inside a newly created directory at the same level.
# The target backup directory names start with time stamps that collate in date/time order.
#
# The instruction file for the above example might contain the following text:
#
#     original    Backup          exclude Backup--*;Backup--*/*
#     original    Benchmark9
#     original    Functional9     exclude out
#     repository  PTS9/pts
#     original    Resources9/OriginalData
#     derived     Resources9/StoredTables
#     repository  SKIRT9/git
#     repository  Web9/git
#
# Lines in the instruction file starting with a \# character are ignored. Other than that, each line causes
# a ZIP archive to be created in the target backup directory. The first token on the line is one of three
# backup characterizations:
#
#   - original: indicates original data that should be backed up frequently.
#   - derived: indicates data that is derived from original data through some (semi-)automated procedure
#     and thus can be backed up somewhat less frequently.
#   - repository: indicates a directory containing a git repository; because the repository is stored on GitHub,
#     it can be backed up somewhat less frequently.
#
# The second token on each line specifies the directory to be backed up, relative to the project parent directory.
# For the \em original and \em derived characterizations, certain files in the nested substructure can be
# excluded by specifying the \em exclude keyword followed by a glob-style pattern. The pattern can have multiple
# sub-patterns separated by a semicolon. Each subpattern is matched to the rightmost portion of the full absolute
# file path.
#
# \note In the current implementation of this script, the tokens (including the directory names and exclusion
# patterns) cannot contain whitespace and cannot be quoted.
#
# By default, the script creates backup archives for all three characterizations. Specifying the \c --derived
# and/or --repos options to have a zero value on the command line suppresses creation of the corresponding archives.
#

# -----------------------------------------------------------------

def do( derived : (int,"backup derived data (specify zero to skip)") = 1,
        repos : (int,"backup repositories (specify zero to skip)") = 1,
        ) -> "create backup archives for the SKIRT/PTS parent project":

    import logging
    import zipfile
    from pts.utils.error import UserError
    import pts.utils.path
    import pts.utils.time

    # get the path to the project parent directory
    projectdir = pts.utils.path.projectParent()

    # create the backup directory
    backupdir = projectdir / "Backup" / ("Backup" + "--" + pts.utils.time.timestamp())
    logging.info("Creating backup directory: {!s}".format(backupdir))
    backupdir.mkdir()

    # open the backup instruction file and read its non-comment lines
    with open(projectdir/"Backup"/"create_backup.txt") as insfile:
        linecount = 0
        for line in insfile:
            if len(line.strip())>0 and not line.strip().startswith('#'):

                # split the line in tokens
                tokens = line.split()
                if len(tokens)!=2 and len(tokens)!=4:
                    raise UserError("Backup instruction line has {} tokens rather than 2 or 4".format(len(tokens)))
                datatype = tokens[0]
                if not datatype in ["original", "derived", "repository"]:
                    raise UserError("Unsupported backup instruction data characterization: '{}'".format(datatype))
                sourcedir = tokens[1]

                # for original and derived, create regular backup archive
                if (datatype=="original") or (datatype=="derived" and derived!=0):

                    # get exclude specification
                    exclude = ""
                    if len(tokens)==4:
                        if tokens[2] != "exclude":
                            raise UserError("Expected 'exclude' in backup instruction line, not '{}'".format(tokens[2]))
                        exclude = tokens[3]

                    # create the archive
                    logging.info("Creating backup for {} data {}...".format(datatype, sourcedir))
                    linecount += 1
                    zipname = backupdir / "{:02d}-{}.zip".format(linecount, sourcedir.replace("/", "-").lower())
                    with zipfile.ZipFile(zipname, mode='w', compression=zipfile.ZIP_DEFLATED,
                                         compresslevel=6) as ziparchive:

                        # include all eligible files
                        for source in (projectdir/sourcedir).rglob("*"):
                            excluded = source.name.startswith(".")
                            if len(exclude)>0: excluded |= any([ source.match(excl) for excl in exclude.split(";") ])
                            if not excluded:
                                logging.info("  Including {}".format(source))
                                ziparchive.write(source, arcname=source.relative_to(projectdir))

                # for repository, pull repository and create archive
                if datatype=="repository" and repos!=0:
                    logging.info("Creating backup for repository {}...".format(sourcedir))
                    linecount += 1
                    zipname = backupdir / "{:02d}-{}-repo.zip".format(linecount, sourcedir.replace("/", "-").lower())
                    with zipfile.ZipFile(zipname, mode='w', compression=zipfile.ZIP_DEFLATED,
                                         compresslevel = 6) as ziparchive:
                        pass

# -----------------------------------------------------------------
