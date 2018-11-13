"""
Least Recently Used page replacement algorithm implementation
"""

import logging

LOG = logging.getLogger(__name__)


class LRU:
    """
    Provides LRU page replacement algorithm implementation
    for given table of pages and trace dataset

    Hit or new item:  add to page table and mark in hash table the memory load #
    Miss:   go through hash table, find lowest #, outright, since numbers are growing, evict it. call add again
    """

    def __init__(self, page_table, trace):
        # set the variables for our algorithm
        self.page_table = page_table
        self.trace = trace
        self.frame_list = page_table.frame_table

        self.initialize_ppns()

        # output variables
        self.hit = False
        self.evict = False
        self.dirty = False

    def initialize_ppns(self):
        """
        Assigns PPNs (Physical Page Numbers) to each frame from page_table.
        """
        counter = 0
        for elem in self.frame_list:
            elem.PPN = counter
            counter += 1

    def add_or_update_successful(self, vpn, read_or_write):
        """
        Takes care of next page in trace
        :param vpn: virtual page number
        :param read_or_write: read or write action
        :return: boolean: hit == true, evict == false
        """
        # first check if we have a hit
        for elem in self.frame_list:
            if elem.VPN == vpn:
                # mark that we had a hit
                self.hit = True

                # add the page
                # set values accordingly
                elem.in_use = True
                elem.VPN = vpn
                # if we're doing a write, need to set dirty bit
                if read_or_write == 'W':
                    elem.dirty = True
                # if we have a READ, mark the last reference variable, so we know that this was the last time our
                # selected VPN was accessed
                else:
                    elem.last_reference = self.page_table.total_memory_accesses
                return True
        else:
            self.hit = False
            # try and add to an empty space, even though we have a page fault
            if not self.add_after_page_fault(vpn, read_or_write):
                # and if that returns false, we need to EVICT and try again
                self.evict = True
                self.evict_page()

            return False

    def add_after_page_fault(self, vpn, read_or_write):
        """
        Adds to an empty space
        :param vpn: virtual page number
        :param read_or_write: read or write action
        :return: boolean: true == page was added, false == all items are in use
        """
        for elem in self.frame_list:
            if not elem.in_use:
                elem.in_use = True
                elem.VPN = vpn
                # if we're doing a write, need to set dirty bit
                if read_or_write == 'W':
                    elem.dirty = True
                else:
                    # if we have a read, mark our reference
                    elem.last_reference = self.page_table.total_memory_accesses
                return True

        # if we make it this far, then all items are in use, so return false
        return False

    def evict_page(self):
        """
        Gets rid of last page
        """
        lowest_value = None
        lowest_value_ppn = 0

        for elem in self.frame_list:
            # index by the key to get a value
            value = elem.last_reference
            # find the lowest value overall, and get its PPN and VPN
            if lowest_value is None or value < lowest_value:
                lowest_value = value
                lowest_value_ppn = elem.PPN

        # remove the lowest value vpn
        self.remove(lowest_value_ppn)

    def remove(self, ppn):
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

    def run_algorithm(self):
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
            next_address = self.trace[0]
            next_vpn = self.page_table.get_vpn(next_address[0])
            next_read_or_write = next_address[1]

            # run it in our algorithm
            if not self.add_or_update_successful(next_vpn, next_read_or_write):
                self.add_after_page_fault(next_vpn, next_read_or_write)

            # then remove it from the trace, so it isn't processed a second time
            self.trace.pop(0)
            self.page_table.total_memory_accesses += 1

            self.print_trace(next_address, next_vpn)

        self.print_results()
        return (len(self.page_table.frame_table), self.page_table.total_memory_accesses,
                self.page_table.page_faults, self.page_table.writes_to_disk)

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

    def print_results(self):
        """
        Prints algorithm final result
        """
        LOG.info("Algorithm: LRU")
        LOG.info("Number of frames:   %s", str(len(self.page_table.frame_table)))
        LOG.info("Total Memory Accesses: %s", str(self.page_table.total_memory_accesses))
        LOG.info("Total Page Faults: %s", str(self.page_table.page_faults))
        LOG.info("Total Writes to Disk: %s", str(self.page_table.writes_to_disk))
