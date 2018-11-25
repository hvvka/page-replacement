"""
Least Recently Used page replacement algorithm implementation
"""
import copy
import logging

import page_table as pt
import result_tuple as rt

LOG = logging.getLogger(__name__)


class LRU:
    """
    Provides LRU page replacement algorithm implementation
    for given table of pages and trace dataset/

    Hit or new item: add to page table and mark in hash table the memory load #.
    Miss: go through hash table, find lowest #, outright, since numbers are growing, evict it.
          Call add again.
    """

    def __init__(self, page_table: pt.PageTable, trace: list, keep_states: bool = False):
        self.page_table: pt.PageTable = page_table
        self.trace: list = trace
        self.frame_list: list = page_table.frame_table

        self.initialize_ppns()

        self.hit: bool = False
        self.evict: bool = False
        self.dirty: bool = False

        self.keep_states: bool = keep_states
        self.table_states: list = []

    def get_table_states(self):
        return self.table_states

    def initialize_ppns(self):
        """
        Assigns PPNs (Physical Page Numbers) to each frame from page_table.
        """
        counter: int = 0
        for elem in self.frame_list:
            elem.ppn = counter
            counter += 1

    def __str__(self) -> str:
        return 'LRU'

    def run_algorithm(self) -> rt.ResultTuple:
        """
        Executes LRU algorithm
        :return: tuple with algorithm final result
        """
        # keep track of our memory accesses
        self.page_table.total_memory_accesses = 0

        # run the algorithm while we have items left in the trace
        while self.trace:
            # reset output variables
            self.hit = False
            self.evict = False
            self.dirty = False

            # pull out next item of the trace
            next_address = self.get_next_address()
            next_vpn = self.page_table.get_vpn(next_address[0])
            next_read_or_write = next_address[1]

            # run it in our algorithm
            if not self.add_or_update_successful(next_vpn, next_read_or_write):
                self.add_after_page_fault(next_vpn, next_read_or_write)

            self.print_trace(next_address, next_vpn)

            if self.keep_states:
                self.table_states.append(copy.deepcopy(self.page_table))

        self.print_results()
        return rt.ResultTuple(len(self.page_table.frame_table), self.page_table.total_memory_accesses,
                              self.page_table.page_faults, self.page_table.writes_to_disk, 'N/A')

    def get_next_address(self):
        """
        Consume current value at trace[0] and remove it from the list.
        :return: next address
        """
        self.page_table.total_memory_accesses += 1
        return self.trace.pop(0)

    def add_or_update_successful(self, vpn, read_or_write):
        """
        Takes care of next page in trace
        :param vpn: virtual page number
        :param read_or_write: read or write action
        :return: boolean: hit == true, evict == false
        """
        if self.is_hit(vpn, read_or_write):
            return True

        self.evict = True
        self.evict_page()

        return False

    def is_hit(self, vpn, read_or_write):
        """
        Checks if there is a hit in page.
        If yes, marks page according to read_or_write.
        :param vpn: virtual page number
        :param read_or_write: access type
        :return: was page in frame table
        """
        for elem in self.frame_list:
            # check for it a hit
            if elem.vpn == vpn:
                self.hit = True
                elem.in_use = True
                elem.vpn = vpn

                if read_or_write == 'W':
                    elem.dirty = True
                elem.last_reference = self.page_table.total_memory_accesses
                return True
        self.hit = False
        return False

    def add_after_page_fault(self, vpn: int, read_or_write: str):
        """
        Adds to an empty space
        :param vpn: virtual page number
        :param read_or_write: read or write action
        :return: boolean: true == page was added, false == all items are in use
        """
        for elem in self.frame_list:
            if not elem.in_use:
                elem.in_use = True
                elem.vpn = vpn
                # if we're doing a write, need to set dirty bit
                if read_or_write == 'W':
                    elem.dirty = True
                elem.last_reference = self.page_table.total_memory_accesses
                return True

        # if we make it this far, then all items are in use, so return false
        return False

    def evict_page(self):
        """
        Gets rid of last page
        """
        lowest_value = None
        lowest_value_ppn: int = 0

        for elem in self.frame_list:
            # index by the key to get a value
            value = elem.last_reference
            # find the lowest value overall, and get its PPN and VPN
            if lowest_value is None or value < lowest_value:
                lowest_value = value
                lowest_value_ppn = elem.ppn

        # remove the lowest value vpn
        self.remove(lowest_value_ppn)

    def remove(self, ppn: int):
        """
        Removes selected ppn from page_table
        :param ppn: physical page number (index)
        """
        removal_page = self.frame_list[ppn]
        # if the page is dirty, we need to do a disk write
        if removal_page.dirty:
            self.dirty = True
        removal_page.in_use = False
        removal_page.dirty = False
        removal_page.vpn = None

    def print_trace(self, next_address, next_vpn):
        """
        Prints result for one page in trace
        :param next_address: next page address
        :param next_vpn: next virtual page number
        """
        if self.hit:
            LOG.debug("Memory address: %s VPN=%s:: number %s \n\t->HIT",
                      str(next_address[0]), str(next_vpn),
                      str(self.page_table.total_memory_accesses))
        elif not self.evict:
            LOG.debug("Memory address: %s VPN=%s:: number %s \n\t->PAGE FAULT - NO EVICTION",
                      str(next_address[0]),
                      str(next_vpn),
                      str(self.page_table.total_memory_accesses))
            self.page_table.page_faults += 1
        elif self.evict and not self.dirty:
            LOG.debug("Memory address: %s VPN=%s:: number %s \n\t->PAGE FAULT - EVICT CLEAN",
                      str(next_address[0]),
                      str(next_vpn),
                      str(self.page_table.total_memory_accesses))
            self.page_table.page_faults += 1
        else:
            LOG.debug("Memory address: %s VPN=%s:: number %s \n\t->PAGE FAULT - EVICT DIRTY",
                      str(next_address[0]),
                      str(next_vpn),
                      str(self.page_table.total_memory_accesses))
            self.page_table.page_faults += 1
            self.page_table.writes_to_disk += 1

        for page in self.page_table.frame_table:
            LOG.debug("%s", page)

    def print_results(self):
        """
        Prints algorithm final result
        """
        LOG.info("Algorithm: LRU")
        LOG.info("Number of frames:      %s", str(len(self.page_table.frame_table)))
        LOG.info("Total Memory Accesses: %s", str(self.page_table.total_memory_accesses))
        LOG.info("Total Page Faults:     %s", str(self.page_table.page_faults))
        LOG.info("Total Writes to Disk:  %s", str(self.page_table.writes_to_disk))
