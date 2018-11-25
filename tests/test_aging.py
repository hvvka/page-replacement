import unittest

import algorithms.aging as aging
import input_parser as parser
import page_table as pt
import tests.test_config as params


class TestAging(unittest.TestCase):
    PATH = './resources/aging.json'

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
        - aging_value
        """
        aging_algorithm = aging.Aging(self.page_table, self.memory_addresses, self.params.refresh,
                                      keep_states=True)
        aging_algorithm.run_algorithm()

        self.assertEqual(10, aging_algorithm.page_table.total_memory_accesses)
        self.assertEqual(9, aging_algorithm.page_table.page_faults)
        self.assertEqual(3, aging_algorithm.page_table.writes_to_disk)

        table_states = aging_algorithm.get_table_states()

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
                self.assertEqual(int(expected_state[frame_index]['aging_value'], 2),
                                 state[frame_index].aging_value)


if __name__ == '__main__':
    unittest.main()
