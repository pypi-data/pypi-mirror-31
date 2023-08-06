"""Simple tests for the base feature generator."""
from __future__ import print_function
from __future__ import absolute_import

import numpy as np
import unittest

from ase.ga.data import DataConnection

from catlearn import __path__ as catlearn_path
from catlearn.fingerprint.base import BaseGenerator
from catlearn.utilities.neighborlist import ase_neighborlist

catlearn_path = '/'.join(catlearn_path[0].split('/')[:-1])


class TestBaseGenerator(unittest.TestCase):
    """Test out base feature generation functions."""

    def test_feature_base(self):
        """Test the base feature generator."""
        gadb = DataConnection('{}/data/gadb.db'.format(catlearn_path))
        all_cand = gadb.get_all_relaxed_candidates()

        f = BaseGenerator()
        nl = ase_neighborlist(all_cand[0])
        assert f.get_neighborlist(all_cand[0]) == nl

        pos = all_cand[0].get_positions()
        assert np.allclose(f.get_positions(all_cand[0]), pos)


if __name__ == '__main__':
    unittest.main()
