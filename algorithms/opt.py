""" 'Opt' (optimal)  Page Replacement Algorithm Implementation
"""
import logging
logger = logging.getLogger(__name__)


class Opt:
    """ An implementation of the optimal page replacement algorithm
    """

    def __init__(self, page_table, trace):
        self.PAGE_TABLE = page_table
        self.trace = trace
        # HashTable, where the KEY=VPN, VALUE=[NUM_LOADS_UNTIL_USED]
        self.time_until_use_dict = {}

        self.hit = False
        self.evict = False
        self.dirty = False

        self.preprocess_trace()

    def get_next_address(self):
        """
        Consume current value at trace[0] and remove it from the list.
        :return: next address
        """
        self.PAGE_TABLE.total_memory_accesses += 1
        return self.trace.pop(0)

    def update_counters(self, vpn):
        """
            need to account for how long until the next memory access of all our current pages
            and this function helps us keep track
        :param vpn:
        """
        # remove the 'next' memory access because it is the CURRENT access, it won't happen in the future
        list_of_memory_accesses = self.time_until_use_dict[vpn]
        if len(list_of_memory_accesses) > 0:
            list_of_memory_accesses.pop(0)
        for frame in self.PAGE_TABLE.frame_table:
            if frame.in_use:
                frame.instructions_until_next_reference -= 1
                if frame.instructions_until_next_reference < -1:  # -1 means we just processed this address
                    frame.instructions_until_next_reference = self.find_time_until_next_access(vpn)

    def find_time_until_next_access(self, vpn):
        """

        :param vpn:
        :return:
        """

        next_index_used = self.time_until_use_dict[vpn][0]  # get the number at index 0

        if next_index_used is None:
            # if None, then time until next access is NEVER, or the current trace length+1, which is effectively 'never'
            time_until_next_access = len(self.trace) + 1
        else:
            # otherwise calculate time until next use by subtracting the total amount of memory accesses,
            # which is the current 'index' of the trace we're on, from the next index at which VPN appears
            time_until_next_access = next_index_used - self.PAGE_TABLE.total_memory_accesses

        return time_until_next_access

    def find_vpn_in_page_table(self, vpn):
        """

        :param vpn:
        :return:
        """
        page_index = None

        # search through and return index if it's there, None if it's not
        index = 0
        for frame in self.PAGE_TABLE.frame_table:
            if frame.VPN == vpn:
                # page_index = index
                return index
            index += 1

        return page_index

    def is_page_fault(self, vpn):
        """

        :param vpn:
        :return:
        """
        if vpn in self.PAGE_TABLE.fast_index:
            return False
        else:
            self.PAGE_TABLE.page_faults += 1
            self.hit = False
            return True

    def add_vpn_to_page_table_or_update(self, vpn, r_or_w):
        """

        :param vpn:
        :param r_or_w:
        :return:
        """

        if vpn in self.PAGE_TABLE.fast_index:
            # iterate through all the frames in the page table, and if there's an empty space, use it
            self.evict = False
            frame_index = self.PAGE_TABLE.fast_index[vpn]
            frame = self.PAGE_TABLE.frame_table[frame_index]
            frame.in_use = True
            frame.dirty = False
            frame.VPN = vpn
            frame.PPN = frame_index
            frame.instructions_until_next_reference = self.find_time_until_next_access(vpn)
            self.PAGE_TABLE.fast_index[vpn] = frame.PPN
            if r_or_w == 'W':
                frame.dirty = True
        else:
            # otherwise, search for a free space
            page_added = False
            index = 0
            for frame in self.PAGE_TABLE.frame_table:
                # then set this frame to in use
                if not frame.in_use:
                    page_added = True
                    frame.in_use = True
                    frame.dirty = False
                    frame.VPN = vpn
                    frame.PPN = index
                    frame.instructions_until_next_reference = self.find_time_until_next_access(vpn)
                    self.PAGE_TABLE.fast_index[vpn] = frame.PPN
                    if r_or_w == 'W':
                        frame.dirty = True
                    break
                index += 1

            if not page_added:
                # if no free pages, then pick a page to evict, and try again
                self.evict_vpn_from_page_table()
                self.add_vpn_to_page_table_or_update(vpn, r_or_w)

    def evict_vpn_from_page_table(self):
        """

        :return:
        """
        least_needed = 0
        most_instructions = 0

        # get time until next reference for ALL pages in our page table currently
        for frame in self.PAGE_TABLE.frame_table:
            # but ONLY launch a search if we don't know how long until next reference yet
            # otherwise, don't search a second or third, etc., time

            # then, use this info to find the least needed VPN overall
            if frame.instructions_until_next_reference > most_instructions:
                least_needed = frame.PPN
                most_instructions = frame.instructions_until_next_reference

        # evict the least needed ppn, and if it's dirty write to disk, increase our disk writes by 1
        removal_frame = self.PAGE_TABLE.frame_table[least_needed]
        self.PAGE_TABLE.fast_index.pop(removal_frame.VPN)
        removal_frame.in_use = False
        removal_frame.VPN = None
        removal_frame.instructions_until_next_reference = None
        if removal_frame.dirty:
            self.PAGE_TABLE.writes_to_disk += 1
            self.evict = True
            self.dirty = True
        else:
            self.evict = True
            self.dirty = False

    def run_algorithm(self):
        """
        :return:
        """
        """ Run the opt algorithm on all memory accesses in the trace
        """

        # pop from the list while we still have elements in it
        while len(self.trace) > 0:
            # set string concatenation variables
            self.hit = False
            self.evict = False
            self.dirty = False

            # get next address and vpn from the trace
            next_address = self.get_next_address()
            next_vpn = self.PAGE_TABLE.get_VPN(next_address[0])

            # update our counters for how many instructions until next usage of all pages in our page table
            self.update_counters(next_vpn)
            # run the algorithm
            self.opt(next_address)

            if self.hit:
                logger.debug("Memory address: " + str(next_address[0]) + " VPN=" + str(next_vpn) + ":: number " + \
                             str(self.PAGE_TABLE.total_memory_accesses) + "\n\t->HIT")
            elif not self.evict:
                logger.debug("Memory address: " + str(next_address[0]) + " VPN=" + str(next_vpn) + ":: number " + \
                             str(self.PAGE_TABLE.total_memory_accesses) + "\n\t->PAGE FAULT - NO EVICTION")
            elif self.evict and not self.dirty:
                logger.debug("Memory address: " + str(next_address[0]) + " VPN=" + str(next_vpn) + ":: number " + \
                             str(self.PAGE_TABLE.total_memory_accesses) + "\n\t->PAGE FAULT - EVICT CLEAN")
            else:
                logger.debug("Memory address: " + str(next_address[0]) + " VPN=" + str(next_vpn) + ":: number " + \
                             str(self.PAGE_TABLE.total_memory_accesses) + "\n\t->PAGE FAULT - EVICT DIRTY")

        self.print_results()

    def opt(self, memory_access):
        """
        :param memory_access:
        :return:
        """
        vpn = self.PAGE_TABLE.get_VPN(memory_access[0])
        read_or_write = memory_access[1]

        if not self.is_page_fault(vpn):
            # no page fault - page is in the table
            if read_or_write == 'W':
                # set dirty bit if writing (W)
                page_index = self.find_vpn_in_page_table(vpn)
                self.PAGE_TABLE.frame_table[page_index].dirty = True
            self.hit = True

        else:
            # page fault

            # if page table isn't full, add next memory address
            # if page table is full, go through the whole list of accesses, and find the VPN that's in memory,
            # which won't be used for the longest time in the future, pick THAT memory address and remove it
            self.add_vpn_to_page_table_or_update(vpn, read_or_write)
            # >>>>>>>>> When we go through the access list for each each page, assign it a value, how long until NEXT
            #          use... then, ONLY search when we don't know how long until next use, for NEW
            #          otherwise subtract 1 from the values we currently have in the table each mem load
            #     if dirty, write to disk, count a disk write

    def print_results(self):
        """
        :return:
        """
        logger.info("Algorithm: Opt")
        logger.info("Number of frames:   " + str(len(self.PAGE_TABLE.frame_table)))
        logger.info("Total Memory Accesses: " + str(self.PAGE_TABLE.total_memory_accesses))
        logger.info("Total Page Faults: " + str(self.PAGE_TABLE.page_faults))
        logger.info("Total Writes to Disk: " + str(self.PAGE_TABLE.writes_to_disk))

    def preprocess_trace(self):
        """
        :return:
        """
        """
          Build a dictionary with the following format: {vpn1: [index_used_1, index_used_2, ..., index_used_n], vpn2: ...}.
          This information should be know before starting the opt algorithm.
        """
        trace_index_number = 0

        for elem in self.trace:
            # get a handle to the vpn at the current index
            vpn = self.PAGE_TABLE.get_VPN(elem[0])

            if vpn in self.time_until_use_dict:
                # add the current index to the list of indices at which our vpn is needed
                self.time_until_use_dict[vpn].append(trace_index_number)
            else:
                # create entry in dictionary
                self.time_until_use_dict[vpn] = [trace_index_number]

            trace_index_number += 1

        for key in self.time_until_use_dict:
            # put a None to the end of the list to signal that this vpn is never used again
            value_list = self.time_until_use_dict[key]
            value_list.append(None)
