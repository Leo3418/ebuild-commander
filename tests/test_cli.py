#  Unit tests for cli.py
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

import unittest
from ebuild_commander.cli import *

import argparse


class TestCli(unittest.TestCase):
    def test_no_arguments(self):
        opts = parse_args([], False)
        self.assertEqual(0, len(opts.scripts[0]))

    def test_single_script(self):
        opts = parse_args(['emerge.sh'], False)
        self.assertEqual(1, len(opts.scripts[0]))

    def test_multiple_scripts(self):
        opts = parse_args(['setup.sh', 'emerge.sh'], False)
        self.assertEqual(2, len(opts.scripts[0]))

    def test_no_portage_configs(self):
        opts = parse_args(['emerge.sh'], False)
        self.assertIsNone(opts.portage_config)

    def test_single_portage_config(self):
        opts = parse_args(['--portage-config', '/etc/portage'], False)
        self.assertEqual(1, len(opts.portage_config))

    def test_multiple_portage_configs(self):
        opts = parse_args(['--portage-config', '/etc/portage',
                           '--portage-config', '~/.config/portage'], False)
        self.assertEqual(2, len(opts.portage_config))
        self.assertEqual(pathlib.Path('/etc/portage'),
                         opts.portage_config[0])
        self.assertEqual(pathlib.Path('~/.config/portage'),
                         opts.portage_config[1])

    def test_threads_non_int(self):
        with self.assertRaises(argparse.ArgumentError):
            parse_args(['--threads', 'I'], False)

    def test_no_custom_repos(self):
        opts = parse_args(['emerge.sh'], False)
        self.assertIsNone(opts.custom_repo)

    def test_single_custom_repo(self):
        opts = parse_args(['--custom-repo', '/var/db/repos/local'], False)
        self.assertEqual(1, len(opts.custom_repo))
        opts = parse_args(['--custom-repo', '/var/db/repos/local',
                           'emerge.sh'], False)
        self.assertEqual(1, len(opts.custom_repo))

    def test_multiple_custom_repos(self):
        opts = parse_args(['--custom-repo', '/var/db/repos/local',
                           '--custom-repo', '/var/db/repos/test'], False)
        self.assertEqual(2, len(opts.custom_repo))
        opts = parse_args(['--custom-repo', '/var/db/repos/local',
                           'emerge.sh',
                           '--custom-repo', '/var/db/repos/test'], False)
        self.assertEqual(2, len(opts.custom_repo))
        self.assertEqual(pathlib.Path('/var/db/repos/local'),
                         opts.custom_repo[0])
        self.assertEqual(pathlib.Path('/var/db/repos/test'),
                         opts.custom_repo[1])

    def test_emerge_opts(self):
        opts = parse_args(['--emerge-opts', '\'--autounmask y\''])
        self.assertEqual('\'--autounmask y\'', opts.emerge_opts)


if __name__ == '__main__':
    unittest.main()
