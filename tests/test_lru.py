import unittest

import algorithms.lru as lru
import input_parser as parser
import page_table as pt


class TestLru(unittest.TestCase):

    def setUp(self):
        num_frames = 8
        file_path = './resources/test.trace'
        self.page_table = pt.PageTable(num_frames)
        self.memory_addresses = parser.parse_trace_file(file_path)
        print(self.page_table)
        print(self.memory_addresses)

    def test_algorithm(self):
        lru_algorithm = lru.LRU(self.page_table, self.memory_addresses)
        lru_algorithm.run_algorithm()


if __name__ == '__main__':
    unittest.main()
