import unittest

import algorithms.opt as opt
import input_parser as parser
import page_table as pt
import tests.test_config as params


class TestOpt(unittest.TestCase):

    def setUp(self):
        self.params = params.PublicParams()
        self.page_table = pt.PageTable(self.params.frames)
        self.memory_addresses = parser.parse_trace_file(self.params.trace_path)

    def test_algorithm(self):
        opt_algorithm = opt.Opt(self.page_table, self.memory_addresses)
        opt_algorithm.run_algorithm()


if __name__ == '__main__':
    unittest.main()
