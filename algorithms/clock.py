"""
Clock page replacement algorithm implementation
"""
import copy
import logging

import circular_queue as cq
import page_table as pt
import result_tuple as rt

LOG = logging.getLogger(__name__)


class Clock:
    """
    Provides clock page replacement algorithm implementation
    for given table of pages and trace dataset
    """

    def __init__(self, page_table: pt.PageTable, trace: list, keep_page_table_states: bool = False):
        self.page_table: pt.PageTable = page_table
        self.trace: list = trace
        self.frame_queue: cq.CircularQueue = page_table.frame_queue

        self.hit: bool = False
        self.evict: bool = False
        self.dirty: bool = False

        self.keep_page_table_states: bool = keep_page_table_states
        self.kept_page_table_states: list = []

    def __str__(self) -> str:
        return 'Clock'

    def run_algorithm(self) -> rt.ResultTuple:
        """
        Performs clock page replacement algorithm
        """
        # Keep track of our memory accesses
        self.page_table.total_memory_accesses = 0

        # Run the algorithm while we have items left in the trace
        while self.trace:
            self.hit = False
            self.evict = False
            self.dirty = False

            # Pull out next item of the trace
            next_address = self.trace[0]
            next_vpn = self.page_table.get_vpn(next_address[0])
            # Run it in our algorithm
            self.add_page_or_update(next_address)
            # Remove it from the trace, so it isn't processed a second time
            self.trace.pop(0)

            self.page_table.total_memory_accesses += 1
            self.print_trace(next_address, next_vpn)

            if self.keep_page_table_states:
                self.kept_page_table_states.append(copy.deepcopy(self.page_table))

        self.print_results()
        return rt.ResultTuple(len(self.page_table.frame_table), self.page_table.total_memory_accesses,
                              self.page_table.page_faults, self.page_table.writes_to_disk, 'N/A')

    def add_page_or_update(self, mem_address):
        """
        Takes care of next page in trace
        :param mem_address: page memory address
        """
        # Try to add a page outright, and if it works, we're done
        vpn = self.page_table.get_vpn(mem_address[0])
        read_or_write = mem_address[1]

        # If we don't successfully add or update...
        if not self.frame_queue.add_or_update_successful(vpn, read_or_write):
            # If we don't find something, then we page fault, and we need to evict a page
            self.page_table.page_faults += 1
            self.evict = True

            victim_frame = self.frame_queue.find_victim()
            victim_frame = self.run_swap_demon(victim_frame)

            self.frame_queue.remove(victim_frame)

            # Add the frame in the newly freed space
            self.frame_queue.add_or_update_successful(vpn, read_or_write)
            self.hit = False

        # Otherwise, we've got a hit
        else:
            self.hit = True

    def run_swap_demon(self, victim_frame):
        """
        Runs swap demon for dirty and unreferenced pages, if necessary.
        Happens when no victim frame is found on first run,
        this also means we are going to write a dirty page to disk when we run the swap daemon.

        :return victim_frame:
        """
        while victim_frame is None:
            # Run the swap daemon, and account for the number of writes to disk
            num_disk_writes = self.frame_queue.flush_dirty_and_unreferenced_pages()
            self.page_table.writes_to_disk += num_disk_writes
            # If we write to disk, we did a dirty eviction
            if num_disk_writes > 0:
                self.dirty = True

            # Get a victim page, since there must be one now that we've flushed
            victim_frame = self.frame_queue.find_victim()
        return victim_frame

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
        elif self.evict and not self.dirty:
            LOG.debug("Memory address: %s VPN=%s:: number %s \n\t->PAGE FAULT - EVICT CLEAN",
                      str(next_address[0]),
                      str(next_vpn),
                      str(self.page_table.total_memory_accesses))
        else:
            LOG.debug("Memory address: %s VPN=%s:: number %s \n\t->PAGE FAULT - EVICT DIRTY",
                      str(next_address[0]),
                      str(next_vpn),
                      str(self.page_table.total_memory_accesses))

    def print_results(self):
        """
        Prints algorithm final result
        """
        LOG.info("Algorithm: Clock")
        LOG.info("Number of frames:      %s", str(len(self.page_table.frame_table)))
        LOG.info("Total Memory Accesses: %s", str(self.page_table.total_memory_accesses))
        LOG.info("Total Page Faults:     %s", str(self.page_table.page_faults))
        LOG.info("Total Writes to Disk:  %s", str(self.page_table.writes_to_disk))
