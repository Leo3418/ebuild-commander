#  ebuild-commander Output Formatting Utilities
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


def info(program_name: str) -> str:
    """
    Apply a color to the program name to indicate an informational message.

    An informational message reports program status and progress that are
    expected during a normal execution.

    :param program_name: the program name, on which a color will be applied
    :return: the program name wrapped in Bash color code for information
    """
    return f'\033[1;36m{program_name}\033[0m'


def warn(program_name: str) -> str:
    """
    Apply a color to the program name to indicate a warning message.

    A warning message reports problems occurred during program execution that
    can be gracefully handled or recovered.  Existence of warning messages
    alone does not result in non-zero exit status.

    :param program_name: the program name, on which a color will be applied
    :return: the program name wrapped in Bash color code for warning
    """
    return f'\033[1;33m{program_name}\033[0m'


def error(program_name: str) -> str:
    """
    Apply a color to the program name to indicate an error message.

    An error message reports serious issues emerged during program execution
    that will cause an abnormal result.  Existence of an error message implies
    non-zero exit status.

    :param program_name: the program name, on which a color will be applied
    :return: the program name wrapped in Bash color code for error
    """
    return f'\033[1;31m{program_name}\033[0m'
