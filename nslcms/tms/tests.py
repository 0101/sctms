from django.test import TestCase

from tms.models import MatchMaker
from tms.utils import is_valid_pairing


class MatchMakerTest(TestCase):

    def _create_players(self, count):
        return [{'player': i+1, 'played_against': ()} for i in range(count)]

    def test_pairing_validation(self):
        p1, p2, p3, p4 = self._create_players(4)

        pairs = [
            [p1, p2],
            [p3, p4],
        ]
        p1['played_against'] = 3, 4
        p2['played_against'] = 3, 4
        p3['played_against'] = 1, 2
        p4['played_against'] = 1, 2

        self.failUnless(is_valid_pairing(pairs))

        p3['played_against'] = 4,
        p4['played_against'] = 3,

        self.failIf(is_valid_pairing(pairs))

        self.failUnless(is_valid_pairing([]))

    def test_fix_rematches(self):
        p1, p2, p3, p4, p5, p6 = self._create_players(6)

        pairs = [
            [p1, p2],
            [p3, p4],
            [p5, p6],
        ]

        p1['played_against'] = 2, 4
        p2['played_against'] = 1, 4, 5
        p4['played_against'] = 1, 2,
        p5['played_against'] = 2,

        pairs = MatchMaker()._fix_rematches(pairs)

        #self.failUnlessEqual(pairs[0][0]['player'], 1)
        #self.failUnlessEqual(pairs[0][1]['player'], 3)
        #
        #self.failUnlessEqual(pairs[1][0]['player'], 2)
        #self.failUnlessEqual(pairs[1][1]['player'], 6)
        #
        #self.failUnlessEqual(pairs[2][0]['player'], 5)
        #self.failUnlessEqual(pairs[2][1]['player'], 4)

        self.failUnlessEqual(len(pairs), 3)
        self.failUnless(is_valid_pairing(pairs))

        pairs[2][0]['played_against'] = pairs[2][1]['player'],
        pairs[2][1]['played_against'] = pairs[2][0]['player'],

        pairs = MatchMaker()._fix_rematches(pairs)

        self.failUnless(is_valid_pairing(pairs))
