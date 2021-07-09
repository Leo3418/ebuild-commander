#  Unit tests for utils.py
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
from ebuild_commander.utils import *


class TestUtils(unittest.TestCase):
    def test_invalid_makeopts(self):
        self.assertEqual(f'MAKEOPTS="-j16"', set_makeopts_num_jobs(
            '', 16))
        self.assertEqual(f'MAKEOPTS="-j16"', set_makeopts_num_jobs(
            'MAKEOPT="-j2"', 16))
        self.assertEqual(f'MAKEOPTS="-j16"', set_makeopts_num_jobs(
            'MAKEOPTS"-j2"', 16))
        self.assertEqual(f'MAKEOPTS="-j16"', set_makeopts_num_jobs(
            'MAKE_OPTS="-j2"', 16))

    def test_short_option(self):
        self.assertEqual(f'MAKEOPTS="-j16"', set_makeopts_num_jobs(
            'MAKEOPTS="-j2"', 16))
        self.assertEqual(f'MAKEOPTS="-j16"', set_makeopts_num_jobs(
            'MAKEOPTS="-j 2"', 16))
        self.assertEqual(f'MAKEOPTS="-j16"', set_makeopts_num_jobs(
            'MAKEOPTS="-j  2"', 16))

    def test_long_option(self):
        self.assertEqual(f'MAKEOPTS="-j16"', set_makeopts_num_jobs(
            'MAKEOPTS="--jobs=2"', 16))
        self.assertEqual(f'MAKEOPTS="-j16"', set_makeopts_num_jobs(
            'MAKEOPTS="--jobs 2"', 16))
        self.assertEqual(f'MAKEOPTS="-j16"', set_makeopts_num_jobs(
            'MAKEOPTS="--jobs  2"', 16))

    def test_multiple_short_options(self):
        self.assertEqual(f'MAKEOPTS="-j16 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="-j2 -j4"', 16))
        self.assertEqual(f'MAKEOPTS="-j16 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="-j 2 -j 4"', 16))
        self.assertEqual(f'MAKEOPTS="-j16 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="-j  2 -j  4"', 16))
        self.assertEqual(f'MAKEOPTS="-j16 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="-j2 -j 4"', 16))
        self.assertEqual(f'MAKEOPTS="-j16 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="-j 2 -j4"', 16))
        self.assertEqual(f'MAKEOPTS="-j16  -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="-j2  -j4"', 16))

    def test_multiple_long_options(self):
        self.assertEqual(f'MAKEOPTS="-j16 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="--jobs=2 --jobs=4"', 16))
        self.assertEqual(f'MAKEOPTS="-j16 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="--jobs 2 --jobs 4"', 16))
        self.assertEqual(f'MAKEOPTS="-j16 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="--jobs  2 --jobs  4"', 16))
        self.assertEqual(f'MAKEOPTS="-j16 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="--jobs=2 --jobs 4"', 16))
        self.assertEqual(f'MAKEOPTS="-j16 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="--jobs 2 --jobs=4"', 16))
        self.assertEqual(f'MAKEOPTS="-j16  -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="--jobs=2  --jobs=4"', 16))

    def test_short_long_options_combo(self):
        self.assertEqual(f'MAKEOPTS="-j16 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="-j2 --jobs=4"', 16))
        self.assertEqual(f'MAKEOPTS="-j16 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="-j 2 --jobs=4"', 16))
        self.assertEqual(f'MAKEOPTS="-j16 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="-j2 --jobs 4"', 16))
        self.assertEqual(f'MAKEOPTS="-j16 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="-j 2 --jobs 4"', 16))

        self.assertEqual(f'MAKEOPTS="-j16 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="--jobs=2 -j4"', 16))
        self.assertEqual(f'MAKEOPTS="-j16 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="--jobs=2 -j 4"', 16))
        self.assertEqual(f'MAKEOPTS="-j16 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="--jobs 2 -j4"', 16))
        self.assertEqual(f'MAKEOPTS="-j16 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="--jobs 2 -j 4"', 16))

        self.assertEqual(f'MAKEOPTS="-j16  -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="-j2  --jobs=4"', 16))
        self.assertEqual(f'MAKEOPTS="-j16  -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="--jobs=2  -j4"', 16))

    def test_invalid_short_option(self):
        self.assertEqual(f'MAKEOPTS="--j16"',
                         set_makeopts_num_jobs('MAKEOPTS="--j 2"', 16))
        self.assertEqual(f'MAKEOPTS="--j16"',
                         set_makeopts_num_jobs('MAKEOPTS="--j2"', 16))
        self.assertEqual(f'MAKEOPTS="-j -j16"',
                         set_makeopts_num_jobs('MAKEOPTS="-j"', 16))

    def test_invalid_long_option(self):
        self.assertEqual(f'MAKEOPTS="-jobs 2 -j16"',
                         set_makeopts_num_jobs('MAKEOPTS="-jobs 2"', 16))
        self.assertEqual(f'MAKEOPTS="-jobs2 -j16"',
                         set_makeopts_num_jobs('MAKEOPTS="-jobs2"', 16))
        self.assertEqual(f'MAKEOPTS="--jobs -j16"',
                         set_makeopts_num_jobs('MAKEOPTS="--jobs"', 16))

    def test_mix_with_other_options(self):
        self.assertEqual(f'MAKEOPTS="-j16 -l2"', set_makeopts_num_jobs(
            'MAKEOPTS="-j2 -l2"', 16))
        self.assertEqual(f'MAKEOPTS="-j16 -l 2"', set_makeopts_num_jobs(
            'MAKEOPTS="-j 2 -l 2"', 16))
        self.assertEqual(
            f'MAKEOPTS="-j16 --load-average=2"', set_makeopts_num_jobs(
                'MAKEOPTS="--jobs=2 --load-average=2"', 16))
        self.assertEqual(
            f'MAKEOPTS="-j16 --load-average 2"', set_makeopts_num_jobs(
                'MAKEOPTS="--jobs 2 --load-average 2"', 16))

        self.assertEqual(f'MAKEOPTS="-l2 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="-l2 -j2"', 16))
        self.assertEqual(f'MAKEOPTS="-l 2 -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="-l 2 -j 2"', 16))
        self.assertEqual(
            f'MAKEOPTS="--load-average=2 -j16"', set_makeopts_num_jobs(
                'MAKEOPTS="--load-average=2 --jobs=2"', 16))
        self.assertEqual(
            f'MAKEOPTS="--load-average 2 -j16"', set_makeopts_num_jobs(
                'MAKEOPTS="--load-average 2 --jobs 2"', 16))

        self.assertEqual(f'MAKEOPTS="-j16  -l2"', set_makeopts_num_jobs(
            'MAKEOPTS="-j2  -l2"', 16))
        self.assertEqual(
            f'MAKEOPTS="-j16  --load-average=2"', set_makeopts_num_jobs(
                'MAKEOPTS="--jobs=2  --load-average=2"', 16))
        self.assertEqual(f'MAKEOPTS="-l2  -j16"', set_makeopts_num_jobs(
            'MAKEOPTS="-l2  -j2"', 16))
        self.assertEqual(
            f'MAKEOPTS="--load-average=2  -j16"', set_makeopts_num_jobs(
                'MAKEOPTS="--load-average=2  --jobs=2"', 16))

    def test_leading_whitespace(self):
        self.assertEqual(f'    MAKEOPTS="-j16"', set_makeopts_num_jobs(
            '    MAKEOPTS="-j2"', 16))

    def test_quotes(self):
        self.assertEqual(f"MAKEOPTS='-j16'", set_makeopts_num_jobs(
            "MAKEOPTS='-j2'", 16))
        self.assertEqual(f"MAKEOPTS='-j16 -l2'", set_makeopts_num_jobs(
            "MAKEOPTS='-j2 -l2'", 16))
        self.assertEqual(f"MAKEOPTS='-l2 -j16'", set_makeopts_num_jobs(
            "MAKEOPTS='-l2 -j2'", 16))
        self.assertEqual(f'MAKEOPTS=-j16', set_makeopts_num_jobs(
            'MAKEOPTS=-j2', 16))
        self.assertEqual(f'MAKEOPTS=-j16 -l2', set_makeopts_num_jobs(
            'MAKEOPTS=-j2 -l2', 16))
        self.assertEqual(f'MAKEOPTS=-l2 -j16', set_makeopts_num_jobs(
            'MAKEOPTS=-l2 -j2', 16))


if __name__ == '__main__':
    unittest.main()
