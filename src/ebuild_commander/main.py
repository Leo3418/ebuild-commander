#  ebuild-commander Main Entry Point Module
#
#  Copyright (C) 2021 Yuan Liao
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

import pathlib
import sys

import ebuild_commander.cli

from ebuild_commander.docker import Commandocker
from ebuild_commander.out_fmt import info, error


def main(program_name: str, args) -> None:
    opts = ebuild_commander.cli.parse_args(args)

    scripts = opts.scripts[0]
    if len(scripts) == 0:
        scripts.append(pathlib.Path('-'))
    custom_repos = opts.custom_repo
    if custom_repos is None:
        custom_repos = []

    container = Commandocker(
        program_name,
        opts.portage_config,
        opts.profile,
        opts.gentoo_repo,
        custom_repos,
        opts.threads,
        opts.emerge_opts,
        opts.docker_image,
        opts.pull,
        opts.storage_opt)
    print(f"{info(program_name)}: Creating Docker container...")
    if not container.start():
        sys.exit(3)

    exit_status = 0
    for script in scripts:
        if script.name == '-':
            in_stream = sys.stdin
            print(f"{info(program_name)}: "
                  f"Reading commands to run from standard input...")
        else:
            try:
                in_stream = open(script)
                print(f"{info(program_name)}: Running script {script}...")
            except OSError as err:
                print(f"{error(program_name)}: {err.filename}: {err.strerror}",
                      file=sys.stderr)
                exit_status = 1
                continue
        for line in in_stream:
            if not container.execute(line):
                exit_status = 1

    print(f"{info(program_name)}: Cleaning up the container...")
    if not container.cleanup():
        exit_status = 3
    sys.exit(exit_status)
