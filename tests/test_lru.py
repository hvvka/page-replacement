import unittest

import algorithms.lru as lru
import input_parser as parser
import page_table as pt
import tests.test_config as params


class TestLru(unittest.TestCase):
    PATH = './resources/lru.json'

    def setUp(self):
        self.params = params.PublicParams()
        self.expected_table_states = params.TableStates(self.PATH)
        self.page_table = pt.PageTable(self.params.frames)
        self.memory_addresses = parser.parse_trace_file(self.params.trace_path)

    def test_algorithm(self):
        """
        Important frame fields:
        - vpn
        - dirty
        - in_use
        - last_reference

        12345678  12345678    12345678    01234567    90123456    a9012345    12345678    ba901234    a9012345    cba90123
                  01234567    01234567    90123456    a9012345    12345678    ba901234    a9012345    cba90123    dcba9012
                              90123456    a9012345    12345678    ba901234    a9012345    cba90123    dcba9012    01234567
        fault     fault       fault       fault       fault       fault       hit         fault       fault       fault
        """
        lru_algorithm = lru.LRU(self.page_table, self.memory_addresses, keep_states=True)
        lru_algorithm.run_algorithm()

        self.assertEqual(10, lru_algorithm.page_table.total_memory_accesses)
        self.assertEqual(9, lru_algorithm.page_table.page_faults)
        self.assertEqual(2, lru_algorithm.page_table.writes_to_disk)

        table_states = lru_algorithm.get_table_states()

        for state_index in range(0, len(table_states)):
            state = table_states[state_index].frame_table
            for frame_index in range(0, len(state)):
                expected_state = self.expected_table_states.get_state(state_index)

                print("\nState: " + str(state_index) + ", frame: " + str(frame_index))
                print(expected_state[frame_index])
                print(state[frame_index])

                self.assertEqual(int(expected_state[frame_index]['vpn']), state[frame_index].vpn)
                self.assertEqual(params.cast_bool(expected_state[frame_index]['dirty']), state[frame_index].dirty)
                self.assertEqual(params.cast_bool(expected_state[frame_index]['in_use']), state[frame_index].in_use)
                self.assertEqual(int(expected_state[frame_index]['last_reference']), state[frame_index].last_reference)


if __name__ == '__main__':
    unittest.main()

