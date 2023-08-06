#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of sbpipe.
#
# sbpipe is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# sbpipe is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with sbpipe.  If not, see <http://www.gnu.org/licenses/>.
#
#
# Object: run a list of tests for the insulin receptor model.
#
# $Revision: 3.0 $
# $Author: Piero Dalle Pezze $
# $Date: 2017-01-31 14:36:32 $

import sys
import os
import unittest
import subprocess

# retrieve SBpipe package path
SBPIPE = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))


class TestPs1Snake(unittest.TestCase):

    _orig_wd = os.getcwd()
    _ir_folder = os.path.join('snakemake')
    _output = 'OK'

    @classmethod
    def setUpClass(cls):
        os.chdir(os.path.join(SBPIPE, 'tests', cls._ir_folder))
        try:
            subprocess.Popen(['CopasiSE'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE).communicate()[0]
        except OSError as e:
            cls._output = 'CopasiSE not found: SKIP ... '
            return
        try:
            subprocess.Popen(['snakemake', '-v'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        except OSError as e:
            cls._output = 'snakemake not found: SKIP ... '

    @classmethod
    def tearDownClass(cls):
        os.chdir(os.path.join(SBPIPE, 'tests', cls._orig_wd))

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_ps1_det1_snake(self):
        if self._output == 'OK':
            from snakemake import snakemake
            self.assertTrue(
                snakemake(os.path.join(SBPIPE, 'sbpipe_ps1.snake'), configfile='ir_model_k1_scan.yaml', cores=7, forceall=True, quiet=True))
        else:
            sys.stdout.write(self._output)
            sys.stdout.flush()

    def test_ps1_det2_snake(self):
        if self._output == 'OK':
            from snakemake import snakemake
            self.assertTrue(
                snakemake(os.path.join(SBPIPE, 'sbpipe_ps1.snake'), configfile='ir_model_ir_beta_inhib.yaml', cores=7, forceall=True, quiet=True))
        else:
            sys.stdout.write(self._output)
            sys.stdout.flush()

    def test_ps1_det3_snake(self):
        if self._output == 'OK':
            from snakemake import snakemake
            self.assertTrue(
                snakemake(os.path.join(SBPIPE, 'sbpipe_ps1.snake'), configfile='ir_model_ir_beta_inhib_overexp.yaml', cores=7, forceall=True, quiet=True))
        else:
            sys.stdout.write(self._output)
            sys.stdout.flush()

    def test_ps1_stoch_snake(self):
        if self._output == 'OK':
            from snakemake import snakemake
            self.assertTrue(
                snakemake(os.path.join(SBPIPE, 'sbpipe_ps1.snake'), configfile='ir_model_ir_beta_inhib_stoch.yaml', cores=7, forceall=True, quiet=True))
        else:
            sys.stdout.write(self._output)
            sys.stdout.flush()


if __name__ == '__main__':
    unittest.main(verbosity=2)
