#  ebuild-commander Main Entry Point Module
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

import os
import pathlib
import shutil
import sys
import time

import ebuild_commander
import ebuild_commander.cli

from ebuild_commander.docker import Commandocker
from ebuild_commander.out_fmt import info, error

_EXIT_SIGINT = 130


def main(program_name: str, args) -> None:
    docker_cmd = os.getenv(ebuild_commander.__env_var_docker__,
                           ebuild_commander.__env_default_docker__)
    if shutil.which(docker_cmd) is None:
        print(f"{error(program_name)}: Executable for Docker functionalities "
              f"'{docker_cmd}' not found", file=sys.stderr)
        sys.exit(3)

    opts = ebuild_commander.cli.parse_args(args)

    scripts = opts.scripts[0]
    if len(scripts) == 0:
        scripts.append(pathlib.Path('-'))
    portage_configs = opts.portage_config
    if portage_configs is None:
        portage_configs = [pathlib.Path('/etc/portage')]
    custom_repos = opts.custom_repo
    if custom_repos is None:
        custom_repos = []

    # Use a canonical container name for this instance to avoid the
    # container from being created twice
    container_name = f'{program_name}-{time.strftime("%Y%m%d-%H%M%S")}'
    container = Commandocker(
        program_name,
        container_name,
        portage_configs,
        opts.profile,
        opts.gentoo_repo,
        custom_repos,
        opts.threads,
        opts.emerge_opts,
        opts.docker_image,
        opts.pull,
        opts.storage_opt,
        docker_cmd
    )

    exit_status = 0
    try:
        print(f"{info(program_name)}: Creating Docker container...",
              file=sys.stderr)
        if not container.start():
            exit_status = 3
        else:
            for script in scripts:
                if script.name == '-':
                    in_stream = sys.stdin
                    print(f"{info(program_name)}: "
                          f"Reading commands to run from standard input...",
                          file=sys.stderr)
                else:
                    try:
                        in_stream = open(script)
                        print(f"{info(program_name)}: "
                              f"Running script {script}...", file=sys.stderr)
                    except OSError as err:
                        print(f"{error(program_name)}: {err.filename}:"
                              f"{err.strerror}", file=sys.stderr)
                        exit_status = 1
                        continue
                for line in in_stream:
                    if not container.execute(line):
                        exit_status = 1
    except KeyboardInterrupt:
        print(f"{error(program_name)}: Exiting on SIGINT", file=sys.stderr)
        exit_status = _EXIT_SIGINT

    should_cleanup = opts.skip_cleanup == 'never' or \
        (opts.skip_cleanup == 'on-fail' and
            (exit_status == 0 or exit_status == _EXIT_SIGINT))
    if should_cleanup:
        print(f"{info(program_name)}: Cleaning up the container...",
              file=sys.stderr)
        if not container.cleanup():
            exit_status = 3
    else:
        print(f"{info(program_name)}: "
              f"Skipping clean-up of container {container_name}",
              file=sys.stderr)

    sys.exit(exit_status)
