import unittest
from pyphoon.io.utils import id2seqno

class TestUtilsMethods(unittest.TestCase):

    def test_id2seqno(self):
        seq_no = id2seqno('200717_2007100618')
        self.assertEqual(seq_no, 200717)
        self.assertIs(type(seq_no), int)
