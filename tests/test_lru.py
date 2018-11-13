import unittest

import algorithms.lru as lru
import input_parser as parser
import page_table as pt
import tests.test_config as params


class TestLru(unittest.TestCase):

    def setUp(self):
        self.params = params.PublicParams()
        self.page_table = pt.PageTable(self.params.frames)
        self.memory_addresses = parser.parse_trace_file(self.params.trace_path)

    def test_algorithm(self):
        lru_algorithm = lru.LRU(self.page_table, self.memory_addresses)
        lru_algorithm.run_algorithm()


if __name__ == '__main__':
    unittest.main()
