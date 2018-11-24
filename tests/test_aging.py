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
        aging_algorithm = aging.Aging(self.page_table, self.memory_addresses, self.params.refresh,
                                      keep_states=True)
        aging_algorithm.run_algorithm()

        self.assertEqual(10, aging_algorithm.page_table.total_memory_accesses)
        self.assertEqual(9, aging_algorithm.page_table.page_faults)
        self.assertEqual(3, aging_algorithm.page_table.writes_to_disk)

        table_states = aging_algorithm.get_table_states()

        ## TODO ##

        # ppn should not change
        for pt in table_states:
            self.assertEqual(0, pt.frame_table[0].ppn)
            self.assertEqual(1, pt.frame_table[1].ppn)
            self.assertEqual(2, pt.frame_table[2].ppn)

        # only frame_table is needed for tests

        # frame_table fields used in AGING algorithm are:
        # - vpn
        # - ppn
        # - dirty
        # - in_use
        # - aging_value

        # address 1.
        ft_01 = table_states[0].frame_table

        self.assertEqual(74565, ft_01[0].vpn)
        self.assertEqual(0, ft_01[1].vpn)
        self.assertEqual(0, ft_01[2].vpn)

        self.assertEqual(False, ft_01[0].dirty)
        self.assertEqual(False, ft_01[1].dirty)
        self.assertEqual(False, ft_01[2].dirty)

        self.assertEqual(True, ft_01[0].in_use)
        self.assertEqual(False, ft_01[1].in_use)
        self.assertEqual(False, ft_01[2].in_use)

        self.assertEqual(int('1000000000000000', 2), ft_01[0].aging_value)
        self.assertEqual(int('0000000000000000', 2), ft_01[1].aging_value)
        self.assertEqual(int('0000000000000000', 2), ft_01[2].aging_value)

        # address 2.
        ft_02 = table_states[1].frame_table

        self.assertEqual(74565, ft_02[0].vpn)
        self.assertEqual(4660, ft_02[1].vpn)
        self.assertEqual(0, ft_02[2].vpn)

        self.assertEqual(False, ft_02[0].dirty)
        self.assertEqual(False, ft_02[1].dirty)
        self.assertEqual(False, ft_02[2].dirty)

        self.assertEqual(True, ft_02[0].in_use)
        self.assertEqual(True, ft_02[1].in_use)
        self.assertEqual(False, ft_02[2].in_use)

        self.assertEqual(int('1000000000000000', 2), ft_02[0].aging_value)
        self.assertEqual(int('1000000000000000', 2), ft_02[1].aging_value)
        self.assertEqual(int('0000000000000000', 2), ft_02[2].aging_value)

        # address 3.
        ft_03 = table_states[2].frame_table

        self.assertEqual(74565, ft_03[0].vpn)
        self.assertEqual(4660, ft_03[1].vpn)
        self.assertEqual(590115, ft_03[2].vpn)

        self.assertEqual(False, ft_03[0].dirty)
        self.assertEqual(False, ft_03[1].dirty)
        self.assertEqual(True, ft_03[2].dirty)

        self.assertEqual(True, ft_03[0].in_use)
        self.assertEqual(True, ft_03[1].in_use)
        self.assertEqual(True, ft_03[2].in_use)

        self.assertEqual(int('0100000000000000', 2), ft_03[0].aging_value)
        self.assertEqual(int('0100000000000000', 2), ft_03[1].aging_value)
        self.assertEqual(int('0100000000000000', 2), ft_03[2].aging_value)

        # address 4.
        ft_04 = table_states[3].frame_table

        self.assertEqual(692242, ft_04[0].vpn)
        self.assertEqual(4660, ft_04[1].vpn)
        self.assertEqual(590115, ft_04[2].vpn)

        self.assertEqual(False, ft_04[0].dirty)
        self.assertEqual(False, ft_04[1].dirty)
        self.assertEqual(True, ft_04[2].dirty)

        self.assertEqual(True, ft_04[0].in_use)
        self.assertEqual(True, ft_04[1].in_use)
        self.assertEqual(True, ft_04[2].in_use)

        self.assertEqual(int('1000000000000000', 2), ft_04[0].aging_value)
        self.assertEqual(int('0100000000000000', 2), ft_04[1].aging_value)
        self.assertEqual(int('0100000000000000', 2), ft_04[2].aging_value)

        # # address 5.
        ft_05 = table_states[4].frame_table

        self.assertEqual(692242, ft_05[0].vpn)
        self.assertEqual(74565, ft_05[1].vpn)
        self.assertEqual(590115, ft_04[2].vpn)

        self.assertEqual(False, ft_05[0].dirty)
        self.assertEqual(True, ft_05[1].dirty)
        self.assertEqual(True, ft_05[2].dirty)

        self.assertEqual(True, ft_05[0].in_use)
        self.assertEqual(True, ft_05[1].in_use)
        self.assertEqual(True, ft_05[2].in_use)

        self.assertEqual(int('1000000000000000', 2), ft_05[0].aging_value)
        self.assertEqual(int('1000000000000000', 2), ft_05[1].aging_value)
        self.assertEqual(int('0100000000000000', 2), ft_05[2].aging_value)

        # address 6.
        ft_06 = table_states[5].frame_table

        self.assertEqual(692242, ft_06[0].vpn)
        self.assertEqual(74565, ft_06[1].vpn)
        self.assertEqual(764161, ft_06[2].vpn)

        self.assertEqual(False, ft_06[0].dirty)
        self.assertEqual(True, ft_06[1].dirty)
        self.assertEqual(False, ft_06[2].dirty)

        self.assertEqual(True, ft_06[0].in_use)
        self.assertEqual(True, ft_06[1].in_use)
        self.assertEqual(True, ft_06[2].in_use)

        self.assertEqual(int('0100000000000000', 2), ft_06[0].aging_value)
        self.assertEqual(int('0100000000000000', 2), ft_06[1].aging_value)
        self.assertEqual(int('0100000000000000', 2), ft_06[2].aging_value)

        # address 7.
        ft_07 = table_states[6].frame_table

        self.assertEqual(692242, ft_07[0].vpn)
        self.assertEqual(74565, ft_07[1].vpn)
        self.assertEqual(764161, ft_07[2].vpn)

        self.assertEqual(False, ft_07[0].dirty)
        self.assertEqual(True, ft_07[1].dirty)
        self.assertEqual(False, ft_07[2].dirty)

        self.assertEqual(True, ft_07[0].in_use)
        self.assertEqual(True, ft_07[1].in_use)
        self.assertEqual(True, ft_07[2].in_use)

        self.assertEqual(int('1100000000000000', 2), ft_07[0].aging_value)
        self.assertEqual(int('0100000000000000', 2), ft_07[1].aging_value)
        self.assertEqual(int('0100000000000000', 2), ft_07[2].aging_value)

        # address 8.
        ft_08 = table_states[7].frame_table

        self.assertEqual(692242, ft_08[0].vpn)
        self.assertEqual(834192, ft_08[1].vpn)
        self.assertEqual(764161, ft_08[2].vpn)

        self.assertEqual(False, ft_08[0].dirty)
        self.assertEqual(True, ft_08[1].dirty)
        self.assertEqual(False, ft_08[2].dirty)

        self.assertEqual(True, ft_08[0].in_use)
        self.assertEqual(True, ft_08[1].in_use)
        self.assertEqual(True, ft_08[2].in_use)

        self.assertEqual(int('1100000000000000', 2), ft_08[0].aging_value)
        self.assertEqual(int('1000000000000000', 2), ft_08[1].aging_value)
        self.assertEqual(int('0100000000000000', 2), ft_08[2].aging_value)

        # address 9.
        ft_09 = table_states[8].frame_table

        self.assertEqual(692242, ft_09[0].vpn)
        self.assertEqual(834192, ft_09[1].vpn)
        self.assertEqual(904105, ft_09[2].vpn)

        self.assertEqual(False, ft_09[0].dirty)
        self.assertEqual(True, ft_09[1].dirty)
        self.assertEqual(False, ft_09[2].dirty)

        self.assertEqual(True, ft_09[0].in_use)
        self.assertEqual(True, ft_09[1].in_use)
        self.assertEqual(True, ft_09[2].in_use)

        self.assertEqual(int('0110000000000000', 2), ft_09[0].aging_value)
        self.assertEqual(int('0100000000000000', 2), ft_09[1].aging_value)
        self.assertEqual(int('0100000000000000', 2), ft_09[2].aging_value)

        # address 10.
        ft_10 = table_states[9].frame_table

        self.assertEqual(692242, ft_10[0].vpn)
        self.assertEqual(4660, ft_10[1].vpn)
        self.assertEqual(904105, ft_10[2].vpn)

        self.assertEqual(False, ft_10[0].dirty)
        self.assertEqual(True, ft_10[1].dirty)
        self.assertEqual(False, ft_10[2].dirty)

        self.assertEqual(True, ft_10[0].in_use)
        self.assertEqual(True, ft_10[1].in_use)
        self.assertEqual(True, ft_10[2].in_use)

        self.assertEqual(int('0110000000000000', 2), ft_10[0].aging_value)
        self.assertEqual(int('1000000000000000', 2), ft_10[1].aging_value)
        self.assertEqual(int('0100000000000000', 2), ft_10[2].aging_value)


if __name__ == '__main__':
    unittest.main()
