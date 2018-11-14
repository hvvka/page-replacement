import unittest

import algorithms.clock as clock
import input_parser as parser
import page_table as pt
import tests.test_config as params


class TestClock(unittest.TestCase):

    def setUp(self):
        self.params = params.PublicParams()
        self.page_table = pt.PageTable(self.params.frames)
        self.memory_addresses = parser.parse_trace_file(self.params.trace_path)

    def test_algorithm(self):
        clock_algorithm = clock.Clock(self.page_table, self.memory_addresses)
        clock_algorithm.run_algorithm()


if __name__ == '__main__':
    unittest.main()