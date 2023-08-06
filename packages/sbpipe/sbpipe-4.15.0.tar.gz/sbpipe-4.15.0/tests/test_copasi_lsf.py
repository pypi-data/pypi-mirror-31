#!/usr/bin/env python
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
# Object: run a list of tests for the insulin receptor model using LSF (Platform Load Sharing Facility)
#
# $Revision: 3.0 $
# $Author: Piero Dalle Pezze $
# $Date: 2016-01-21 10:36:32 $

import os
import sys
# retrieve SBpipe package path
SBPIPE = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
sys.path.append(SBPIPE)
import sbpipe.main as sbmain
import unittest
import subprocess


class TestCopasiLSF(unittest.TestCase):

    _orig_wd = os.getcwd()  # remember our original working directory
    _ir_folder = os.path.join('lsf')
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
            subprocess.Popen(['bjobs'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE).communicate()[0]
        except OSError as e:
            cls._output = 'LSF not found: SKIP ... '

    @classmethod
    def tearDownClass(cls):
        os.chdir(os.path.join(SBPIPE, 'tests', cls._orig_wd))

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_stoch_sim_copasi_lsf(self):
        if self._output == 'OK':
            self.assertEqual(sbmain.sbpipe(simulate="lsf_ir_model_stoch_simul.yaml", quiet=True), 0)
        else:
            sys.stdout.write(self._output)
            sys.stdout.flush()

    def test_pe_copasi_lsf(self):
        if self._output == 'OK':
            self.assertEqual(sbmain.sbpipe(parameter_estimation="lsf_ir_model_param_estim.yaml", quiet=True), 0)
        else:
            sys.stdout.write(self._output)
            sys.stdout.flush()
            
    def test_stoch_pe_copasi_lsf(self):
        if self._output == 'OK':
            self.assertEqual(sbmain.sbpipe(parameter_estimation="lsf_ir_model_stoch_param_estim.yaml", quiet=True), 0)
        else:
            sys.stdout.write(self._output)
            sys.stdout.flush()

    def test_stoch_ps1_copasi_lsf(self):
        if self._output == 'OK':
            self.assertEqual(sbmain.sbpipe(parameter_scan1="lsf_ir_model_ir_beta_inhib_stoch.yaml", quiet=True), 0)
        else:
            sys.stdout.write(self._output)
            sys.stdout.flush()

    def test_stoch_ps2_copasi_lsf(self):
        if self._output == 'OK':
            self.assertEqual(sbmain.sbpipe(parameter_scan2="lsf_ir_model_insulin_ir_beta_dbl_stoch_inhib.yaml", quiet=True), 0)
        else:
            sys.stdout.write(self._output)
            sys.stdout.flush()


if __name__ == '__main__':
    unittest.main(verbosity=2)
