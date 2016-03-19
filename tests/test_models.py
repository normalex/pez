from unittest import TestCase

from test_common import FreshSchemaTestCase

from pez.models import (
    MAXUINT64, forward_sequence, backward_sequence, session_scope
)
from pez.config import configuration


class TestForwardSequencer(FreshSchemaTestCase):

    def test_forward_seq_shall_cycle_on_max(self):
        with session_scope() as sess:
            sess.execute(
                'select setval(:regclass, :val, false);',
                dict(
                    regclass=str(forward_sequence.name),
                    val=MAXUINT64
                )
            )
            max_uint = sess.execute(forward_sequence)
            cycled_uint = sess.execute(forward_sequence)
        self.assertEqual(max_uint, MAXUINT64)
        self.assertEqual(cycled_uint, 1)

    def test_backward_seq_shall_cycle_on_min(self):
        with session_scope() as sess:
            sess.execute(
                'select setval(:regclass, :val, false);',
                dict(
                    regclass=str(backward_sequence.name),
                    val=1
                )
            )
            min_uint = sess.execute(backward_sequence)
            cycled_uint = sess.execute(backward_sequence)
        self.assertEqual(min_uint, 1)
        self.assertEqual(cycled_uint, MAXUINT64)

