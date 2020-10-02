# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 15:07:16 2017

@author: Suhas Somnath
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
import unittest
import warnings

import numpy as np
from numpy.testing import assert_array_equal, assert_allclose
from sidpy.sid.dimension import Dimension

sys.path.append("../../sidpy/")

if sys.version_info.major == 3:
    unicode = str


class TestDimension(unittest.TestCase):

    def test_values_as_array(self):
        name = 'Bias'
        values = np.random.rand(5)

        descriptor = Dimension(values, name)
        for expected, actual in zip([name, values],
                                    [descriptor.name, descriptor.values]):
            self.assertTrue(np.all([x == y for x, y in zip(expected, actual)]))

    def test_values_as_length(self):
        name = 'Bias'
        units = 'V'
        values = np.arange(5)

        descriptor = Dimension(len(values), name, units=units)
        for expected, actual in zip([name, units],
                                    [descriptor.name, descriptor.units]):
            self.assertTrue(np.all([x == y for x, y in zip(expected, actual)]))
        self.assertTrue(np.allclose(values, descriptor.values))

    def test_copy(self):
        name = 'Bias'
        units = 'V'
        values = np.arange(5)

        descriptor = Dimension(values, name, units=units)
        copy_descriptor = descriptor.copy()

        for expected, actual in zip([copy_descriptor.name, copy_descriptor.units],
                                    [descriptor.name, descriptor.units]):
            self.assertTrue(np.all([x == y for x, y in zip(expected, actual)]))
        self.assertTrue(np.allclose(copy_descriptor.values, descriptor.values))
        copy_descriptor.units = 'eV'
        copy_descriptor.name = 'energy'
        for expected, actual in zip([copy_descriptor.name, copy_descriptor.units],
                                    [descriptor.name, descriptor.units]):
            self.assertTrue(np.all([x != y for x, y in zip(expected, actual)]))
        copy_descriptor = descriptor +1
        self.assertFalse(np.allclose(copy_descriptor.values, descriptor.values))

    def test_repr(self):
        name = 'Bias'
        values = np.arange(5)

        descriptor = Dimension(values, name)
        actual = '{}'.format(descriptor)
        quantity = 'generic'
        units = 'generic'
        expected = '{}:  {} ({}) of size {}'.format(name, quantity, units, values.shape)
        self.assertEqual(actual, expected)


    def test_inequality_req_inputs(self):
        name = 'Bias'
        units='nm'

        self.assertTrue(Dimension([0, 1, 2, 3], name) == Dimension([0, 1, 2, 3], name))
        self.assertFalse(Dimension([0, 1, 2, 3], 'fdfd') == Dimension([0, 1, 2, 3], name))
        self.assertFalse(Dimension([0, 1, 2], name) == Dimension([0, 1, 2, 3], name))

        self.assertTrue(Dimension([0, 1, 2, 3], name, units) == Dimension([0, 1, 2, 3], name, units))
        self.assertFalse(Dimension([0, 1, 2, 3], name, 'pm') == Dimension([0, 1, 2, 3], name, units))
        self.assertFalse(Dimension([0, 1, 2], name, units) == Dimension([0, 1, 2, 3], name, units))

    def test_dimensionality(self):
        vals = np.ones((2, 2))
        expected = 'Dimension can only be 1 dimensional'
        with self.assertRaises(Exception) as context:
            _ = Dimension(vals, "x",)
        self.assertTrue(expected in str(context.exception))

    def test_info(self):
        expected = "X - Bias (mV): [0. 1. 2. 3. 4.]"
        dim = Dimension(np.arange(5), "X", "Bias", "mV")
        self.assertTrue(dim.info, expected)

    def test_nonposint_values(self):
        vals = [-1, []]
        expected = 2*["values should at least be specified as a positive integer"]
        for v, e in zip(vals, expected):
            with self.assertRaises(TypeError) as context:
                _ = Dimension(v, "x")
            self.assertTrue(e in str(context.exception))

    def test_conv2arr_values(self):
        arr = np.arange(5)
        vals = [5, arr, arr.tolist(), tuple(arr)]
        vals_expected = arr
        for v in vals:
            dim = Dimension(v, "x")
            self.assertIsInstance(dim,  Dimension)
            assert_array_equal(np.array(dim), vals_expected)

    def test_dimension_type(self):
        dim_types = ["spatial", "Spatial", "reciprocal", "Reciprocal",
                     "spectral", "Spectral", "temporal", "Temporal",
                     "frame", "Frame",  "time", "Time", "stack", "Stack"]
        dim_vals_expected = [1, 1, 2, 2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4]
        dim_names_expected = ["SPATIAL", "SPATIAL", "RECIPROCAL", "RECIPROCAL",
                              "SPECTRAL", "SPECTRAL", "TEMPORAL", "TEMPORAL",
                              "TEMPORAL", "TEMPORAL", "TEMPORAL", "TEMPORAL",
                              "TEMPORAL", "TEMPORAL"]
        for dt, dv, dn in zip(dim_types, dim_vals_expected, dim_names_expected):
            dim = Dimension(5, "x", dimension_type=dt)
            self.assertEqual(dim.dimension_type.value, dv)
            self.assertEqual(dim.dimension_type.name, dn)

    def test_unknown_dimension_type(self):
        dim_type = "bad_name"
        expected_wrn = ["Supported dimension types for plotting are only: [",
                        "Setting DimensionType to UNKNOWN"]
        with warnings.catch_warnings(record=True) as w:
            _ = Dimension(5, "x", dimension_type=dim_type)
        self.assertTrue(expected_wrn[0] in str(w[0].message))
        self.assertTrue(expected_wrn[1] in str(w[1].message))
