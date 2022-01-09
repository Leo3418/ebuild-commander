#  Utility Functions for ebuild-commander
#
#  Copyright (C) 2021-2022 Yuan Liao
#
#  This file is part of ebuild-commander.
#
#  ebuild-commander is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  ebuild-commander is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ebuild-commander.  If not, see
#  <https://www.gnu.org/licenses/>.

import re


def set_makeopts_num_jobs(line: str, num_jobs: int) -> str:
    """
    Modify a line from `/etc/portage/make.conf` which defines `MAKEOPTS`, so it
    sets the `-j` option with the specified number of jobs.

    If any `-j` or `--jobs` options have already been set, they will all be
    replaced by the new `-j` option.

    If no `-j` or `--jobs` option exists, then a new `-j` option will be added.

    If the line provided does not seem to be a valid `MAKEOPTS` definition,
    then it will be ignored, and a new `MAKEOPTS` definition with only the `-j`
    option set will be returned.

    :param line: the original line containing a `MAKEOPTS` definition
    :param num_jobs: the desired number of jobs to be set
    :return: a new `MAKEOPTS` definition which sets the `-j` option and can be
        directly added as a line to `/etc/portage/make.conf`
    """
    makeopts_prefix = 'MAKEOPTS='
    if line.lstrip().startswith(makeopts_prefix):
        # Modify any existing -j/--jobs settings
        new_makeopts, num_repl = re.subn(r'(-j *|--jobs( *|=))[0-9]+',
                                         f'-j{num_jobs}', line)
        if num_repl <= 0:
            # No -j/--jobs settings in MAKEOPTS; append the flag to it
            rstripped_makeopts = line.rstrip()
            if rstripped_makeopts.endswith("'"):
                new_makeopts = rstripped_makeopts[:-1]
                new_makeopts += f' -j{num_jobs}'
                new_makeopts += "'"
            elif rstripped_makeopts.endswith('"'):
                new_makeopts = rstripped_makeopts[:-1]
                new_makeopts += f' -j{num_jobs}'
                new_makeopts += '"'
            else:
                new_makeopts = f'{rstripped_makeopts} -j{num_jobs}'
    else:
        # MAKEOPTS is unset; directly set a new value
        new_makeopts = f'{makeopts_prefix}"-j{num_jobs}"'
    return new_makeopts
