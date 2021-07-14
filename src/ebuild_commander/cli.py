#  ebuild-commander Command-line Interface Module
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

import argparse
import os
import pathlib

import ebuild_commander


def parse_args(args, exit_on_error: bool = True) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]... [SCRIPT]...",
        description="""
Run the SCRIPTs in a Docker container derived from a Gentoo stage3 image.
With no SCRIPT, or when SCRIPT is -, read standard input.\
        """,
        epilog="""
exit status:
  0 if OK,
  1 if minor problems (e.g. cannot access any SCRIPT),
  2 if unrecognized arguments,
  3 if serious trouble (e.g. cannot run a Docker command).\
        """,
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
        exit_on_error=exit_on_error
    )

    parser.add_argument(
        'scripts',
        type=pathlib.Path,
        nargs='*',
        action='append',
        help=argparse.SUPPRESS
    )

    parser.add_argument(
        '--portage-config',
        metavar='DIR',
        type=pathlib.Path,
        action='append',
        help="copy configuration in DIR to container's /etc/portage,\n"
             "ignoring make.profile and repos.conf; can be set\n"
             "repeatedly to overlay configuration directories on top\n"
             "of directories specified earlier in the command\n"
             "(default: /etc/portage if this option is never used)"
    )
    parser.add_argument(
        '--profile',
        metavar='TARGET',
        default='default/linux/amd64/17.1',
        help="run 'eselect profile set TARGET' when container starts\n"
             "(default: %(default)s)"
    )
    parser.add_argument(
        '--gentoo-repo',
        metavar='DIR',
        type=pathlib.Path,
        default='/var/db/repos/gentoo',
        help="use Gentoo repository at DIR\n"
             "(default: %(default)s)"
    )
    parser.add_argument(
        '--custom-repo',
        metavar='DIR',
        type=pathlib.Path,
        action='append',
        help="add a custom ebuild repository at DIR\n"
             "(can be set repeatedly to use multiple repositories)"
    )
    parser.add_argument(
        '--threads',
        metavar='JOBS',
        type=int,
        default=os.cpu_count(),
        help="specify '-j JOBS' in MAKEOPTS\n"
             "(default: number of CPU threads)"
    )
    parser.add_argument(
        '--emerge-opts',
        metavar='OPTS',
        default='--color y --verbose',
        help="run emerge with OPTS added to command-line arguments\n"
             "(default: %(default)s)"
    )

    parser.add_argument(
        '--docker-image',
        metavar='IMAGE',
        default='gentoo/stage3',
        help="create the container from the specified Docker IMAGE\n"
             "(default: %(default)s)"
    )
    parser.add_argument(
        '--pull',
        action='store_true',
        help="download the latest version of the Docker image"
    )
    parser.add_argument(
        '--storage-opt',
        metavar='OPTS',
        help="set '--storage-opt OPTS' in Docker's arguments"
    )

    parser.add_argument(
        '--skip-cleanup',
        choices=['always', 'on-fail', 'never'],
        default='on-fail',
        help="skip container clean-up before exiting\n"
             "(default: %(default)s)"
    )

    parser.add_argument(
        '--help',
        action='help',
        help="display this help and exit"
    )
    parser.add_argument(
        '--version',
        action='version',
        help='output version information and exit',
        version=get_version_message()
    )

    opts = parser.parse_args(args)
    return opts


def get_version_message() -> str:
    return f"""
ebuild-commander {ebuild_commander.__version__}
Copyright (C) 2021 Yuan Liao
License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.\
    """
