"""
Aging page replacement algorithm implementation
"""

import logging

import result_tuple as rt

LOG = logging.getLogger(__name__)


class Aging:
    """
    An implementation of the aging page replacement algorithm
    """
    COUNTER_LENGTH = 16

    def __init__(self, page_table, trace, refresh_rate):
        self.page_table = page_table
        self.trace = trace
        self.frame_queue = page_table.frame_table

        self.hit = False
        self.evict = False
        self.dirty = False

        index = 0
        for elem in self.frame_queue:
            elem.ppn = index
            index += 1

        # refresh variables for aging
        self.refresh_time_in_processed_instructions = refresh_rate
        self.time_of_last_refresh = 0

    def __str__(self) -> str:
        return 'Aging'

    def shift_age_counter(self):
        """
        Shifts counters (performs aging).
        Assumption: counter is COUNTER_LENGTH-bit.
        """
        for elem in self.frame_queue:
            elem.aging_value >>= 1

    def collect_data_on_references_during_this_tick(self):
        """
        Checks if it is time to refresh counters.
        If yes, performs counters shifting depending on reference bit, updates time to refresh value
        and resets reference bits.
        """
        self.time_of_last_refresh += 1

        for elem in self.frame_queue:
            # update most significant bit if referenced
            if elem.reference is True:
                elem.aging_value |= (1 << (Aging.COUNTER_LENGTH - 1))
                elem.reference = False

        if self.time_of_last_refresh >= self.refresh_time_in_processed_instructions:
            self.shift_age_counter()
            self.time_of_last_refresh = 0

    def is_hit(self, vpn, read_or_write):
        """
        Checks if there is a hit in page.
        If yes, marks page according to read_or_write.
        :param vpn:
        :param read_or_write:
        :return:
        """
        for elem in self.frame_queue:
            # check for it a hit
            if elem.vpn == vpn:
                self.hit = True

                if read_or_write == 'W':
                    elem.dirty = True
                elem.reference = True
                return True
        return False

    def was_empty_page_used(self, vpn, read_or_write):
        """
        Looks for an empty page and if found, uses it
        :return:
        """
        for elem in self.frame_queue:
            if not elem.in_use:
                elem.in_use = True
                elem.vpn = vpn
                if read_or_write == 'W':
                    elem.dirty = True
                elem.reference = True
                return True
        return False

    def add_or_update_page(self, vpn, read_or_write):
        """
        Tries to add/update a page. If not possible, evicts a page.
        :param vpn:
        :param read_or_write:
        """
        if self.is_hit(vpn, read_or_write):
            return
        if self.was_empty_page_used(vpn, read_or_write):
            return

        # otherwise page table is full and there is need to evict a page with lowest value
        lowest_value_page_number = 0
        # higher than highest value in the COUNTER_LENGTH-bit counter
        lowest_value_overall = 2 ** Aging.COUNTER_LENGTH

        for elem in self.frame_queue:
            if elem.aging_value < lowest_value_overall:
                lowest_value_page_number = elem.ppn
                lowest_value_overall = elem.aging_value

        self.evict_lowest_value_page(lowest_value_page_number)
        if not self.was_empty_page_used(vpn, read_or_write):
            raise Exception("There should have been an empty page used!")

    def evict_lowest_value_page(self, ppn):
        """
        Evicts page with lowest page value.
        :param ppn: index in frame_queue holding page to evict
        """
        page = self.frame_queue[ppn]
        self.evict = True

        if page.dirty:
            self.dirty = True
            self.page_table.writes_to_disk += 1
        self.remove(ppn)

    def remove(self, ppn):
        """
        Removes page from page table with given page table index.
        :param ppn:
        """
        removal_page = self.frame_queue[ppn]
        removal_page.aging_value = 0
        removal_page.in_use = False
        removal_page.reference = False
        removal_page.dirty = False
        removal_page.vpn = None

    def get_next_address(self):
        """
        Consume current value at trace[0] and remove it from the list.
        :return: next address
        """
        self.page_table.total_memory_accesses += 1
        return self.trace.pop(0)

    def run_algorithm(self) -> rt.ResultTuple:
        """
        Processes each instruction and runs aging algorithm
        :return: ResultTuple
        """
        while self.trace:
            self.hit = False
            self.evict = False
            self.dirty = False

            next_address = self.get_next_address()
            next_vpn = self.page_table.get_vpn(next_address[0])
            next_read_or_write = next_address[1]

            self.add_or_update_page(next_vpn, next_read_or_write)
            self.collect_data_on_references_during_this_tick()

            if self.hit:
                LOG.debug("Memory address: %s VPN=%s:: number %s \n\t->HIT",
                          next_address[0],
                          next_vpn,
                          self.page_table.total_memory_accesses)
            elif not self.evict:
                LOG.debug("Memory address: %s VPN=%s:: number %s \n\t->PAGE FAULT - NO EVICTION",
                          next_address[0],
                          next_vpn,
                          self.page_table.total_memory_accesses)
                self.page_table.page_faults += 1
            elif self.evict and not self.dirty:
                LOG.debug("Memory address: %s VPN=%s:: number %s \n\t->PAGE FAULT - EVICT CLEAN",
                          next_address[0],
                          next_vpn,
                          self.page_table.total_memory_accesses)
                self.page_table.page_faults += 1
            else:
                LOG.debug("Memory address: %s VPN=%s:: number %s \n\t->PAGE FAULT - EVICT DIRTY",
                          next_address[0],
                          next_vpn,
                          self.page_table.total_memory_accesses)
                self.page_table.page_faults += 1

            LOG.debug("Frame table:")
            for page in self.frame_queue:
                LOG.debug("%s", page)
            LOG.debug("")

        self.print_results()
        return rt.ResultTuple(len(self.page_table.frame_table), self.page_table.total_memory_accesses,
                              self.page_table.page_faults, self.page_table.writes_to_disk,
                              self.refresh_time_in_processed_instructions)

    def print_results(self):
        LOG.info("Algorithm: Aging")
        LOG.info("Number of frames:      %s", len(self.page_table.frame_table))
        LOG.info("Refresh Rate:          %s", self.refresh_time_in_processed_instructions)
        LOG.info("Total Memory Accesses: %s", self.page_table.total_memory_accesses)
        LOG.info("Total Page Faults:     %s", self.page_table.page_faults)
        LOG.info("Total Writes to Disk:  %s", self.page_table.writes_to_disk)
