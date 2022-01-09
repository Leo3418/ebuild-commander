#  ebuild-commander Main Package Initialization File
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

# The program's version -- please change this when releasing a new version
__version__ = '0.1.0'

# The name of the environment variable that specifies the executable providing
# Docker functionalities this program should use
__env_var_docker__ = 'EBUILD_CMDER_DOCKER'

# The default value for the environment variable corresponding to
# __env_var_docker
__env_default_docker__ = 'docker'
