"""
OPT (optimal) page replacement algorithm implementation
"""
import logging

LOG = logging.getLogger(__name__)


class Opt:
    """
    An implementation of the optimal page replacement algorithm
    """

    def __init__(self, page_table, trace):
        self.page_table = page_table
        self.trace = trace
        # KEY = VPN, VALUE = [NUM_LOADS_UNTIL_USED]
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
        self.page_table.total_memory_accesses += 1
        return self.trace.pop(0)

    def update_counters(self, vpn):
        """
        Update our counters for how many instructions until next usage of all pages in our page table.
        Pops vpn usage from time_until_use_dict, decrements PAGE_TABLE.frame_table "in_use" frames.
        updates counters in PAGE_TABLE.
        frame.instructions_until_next_reference < -1: means that this address was just processed
        :param vpn: virtual page number
        """
        list_of_memory_accesses = self.time_until_use_dict[vpn]
        if len(list_of_memory_accesses) > 0:
            list_of_memory_accesses.pop(0)
        for frame in self.page_table.frame_table:
            if frame.in_use:
                frame.instructions_until_next_reference -= 1
                if frame.instructions_until_next_reference < -1:
                    frame.instructions_until_next_reference = self.find_time_until_next_access(vpn)

    def find_time_until_next_access(self, vpn):
        """
        Checks if there is a next index in index queue for a vpn. If there is not, then time until next access is never
        (current trace length + 1). Otherwise time until next access is calculated by subtracting the total amount
        of memory accesses, which is the current 'index' of the current trace, from the next index at which VPN appears
        :param vpn: virtual page number
        :return: time until next access
        """
        next_index_used = self.time_until_use_dict[vpn][0]  # get the number at index 0
        if next_index_used is None:
            time_until_next_access = len(self.trace) + 1
        else:
            time_until_next_access = next_index_used - self.page_table.total_memory_accesses
        return time_until_next_access

    def find_vpn_in_page_table(self, vpn):
        """
        Finds virtual page number in page table. Return None if vpn is not found.
        :param vpn: virtual page number
        :return: page_index:
        """
        page_index = None
        index = 0
        for frame in self.page_table.frame_table:
            if frame.vpn == vpn:
                return index
            index += 1
        return page_index

    def is_page_fault(self, vpn):
        """
        Checks if page fault occurred. If not, updates "hit" instance variable and increments page faults counter.
        Otherwise, search for a free space
        :param vpn: virtual page number
        :return: boolean
        """
        if vpn in self.page_table.fast_index:
            return False
        else:
            self.page_table.page_faults += 1
            self.hit = False
            return True

    def add_vpn_to_page_table_or_update(self, vpn, r_or_w):
        """
        If there is a page fault:
        - if page table isn't full, add next memory address
        - if page table is full, go through the whole list of accesses, and find the VPN that's in memory,
          which won't be used for the longest time in the future, pick that memory address and remove it

        When going through the access list for each each page, assign it a value, how long until NEXT
        use. Then, perform search only if it is unknown how long until next use,
        for new otherwise subtract 1 from the values in the table each mem load
        if dirty, write to disk, count a disk write

        Checks if vpn is already in PAGE_TABLE.
        If it is, iterate through all the frames in the page table, and if there's an empty space, use it.
        :param vpn: virtual page number
        :param r_or_w: read or write type of access
        """

        if vpn in self.page_table.fast_index:
            self.evict = False
            frame_index = self.page_table.fast_index[vpn]
            frame = self.page_table.frame_table[frame_index]
            frame.in_use = True
            frame.dirty = False
            frame.vpn = vpn
            frame.ppn = frame_index
            frame.instructions_until_next_reference = self.find_time_until_next_access(vpn)
            self.page_table.fast_index[vpn] = frame.ppn
            if r_or_w == 'W':
                frame.dirty = True
        else:
            page_added = False
            index = 0
            for frame in self.page_table.frame_table:
                if not frame.in_use:
                    page_added = True
                    frame.in_use = True
                    frame.dirty = False
                    frame.vpn = vpn
                    frame.ppn = index
                    frame.instructions_until_next_reference = self.find_time_until_next_access(vpn)
                    self.page_table.fast_index[vpn] = frame.ppn
                    if r_or_w == 'W':
                        frame.dirty = True
                    break
                index += 1

            if not page_added:
                self.evict_vpn_from_page_table()
                self.add_vpn_to_page_table_or_update(vpn, r_or_w)

    def evict_vpn_from_page_table(self):
        """
        Iterates over all frames and finds frame with biggest instructions_until_next_reference value
        as well as least needed PPN. Removes this page.
        If page is dirty, increases disk writes by 1.
        """
        least_needed = 0
        most_instructions = 0

        for frame in self.page_table.frame_table:
            if frame.instructions_until_next_reference > most_instructions:
                least_needed = frame.ppn
                most_instructions = frame.instructions_until_next_reference

        removal_frame = self.page_table.frame_table[least_needed]
        self.page_table.fast_index.pop(removal_frame.vpn)
        removal_frame.in_use = False
        removal_frame.vpn = None
        removal_frame.instructions_until_next_reference = None
        if removal_frame.dirty:
            self.page_table.writes_to_disk += 1
            self.evict = True
            self.dirty = True
        else:
            self.evict = True
            self.dirty = False

    def run_algorithm(self):
        """
        Run the opt algorithm on all memory accesses in the trace
        :return:
        """
        while len(self.trace) > 0:
            self.hit = False
            self.evict = False
            self.dirty = False

            next_address = self.get_next_address()
            next_vpn = self.page_table.get_vpn(next_address[0])

            self.update_counters(next_vpn)
            self.opt(next_address)

            if self.hit:
                LOG.debug("Memory address: " + str(next_address[0]) + " VPN=" + str(next_vpn) + ":: number " + \
                          str(self.page_table.total_memory_accesses) + "\n\t->HIT")
            elif not self.evict:
                LOG.debug("Memory address: " + str(next_address[0]) + " VPN=" + str(next_vpn) + ":: number " + \
                          str(self.page_table.total_memory_accesses) + "\n\t->PAGE FAULT - NO EVICTION")
            elif self.evict and not self.dirty:
                LOG.debug("Memory address: " + str(next_address[0]) + " VPN=" + str(next_vpn) + ":: number " + \
                          str(self.page_table.total_memory_accesses) + "\n\t->PAGE FAULT - EVICT CLEAN")
            else:
                LOG.debug("Memory address: " + str(next_address[0]) + " VPN=" + str(next_vpn) + ":: number " + \
                          str(self.page_table.total_memory_accesses) + "\n\t->PAGE FAULT - EVICT DIRTY")

        self.print_results()
        result_tup = (len(self.page_table.frame_table), self.page_table.total_memory_accesses,
                      self.page_table.page_faults, self.page_table.writes_to_disk)
        return result_tup

    def opt(self, memory_access):
        """
        Performs OPT algorithm for a next VPN.
        Checks if there is not a page fault (page is in the table, hit).
        If it is, add_vpn_to_page_table_or_update.
        :param memory_access: tuple (vpn, r/w)
        """
        vpn = self.page_table.get_vpn(memory_access[0])
        read_or_write = memory_access[1]

        if not self.is_page_fault(vpn):
            if read_or_write == 'W':
                page_index = self.find_vpn_in_page_table(vpn)
                self.page_table.frame_table[page_index].dirty = True
            self.hit = True
        else:
            self.add_vpn_to_page_table_or_update(vpn, read_or_write)

    def print_results(self):
        """
        Prints algorithm results on the screen
        """
        LOG.info("Algorithm: Opt")
        LOG.info("Number of frames:   " + str(len(self.page_table.frame_table)))
        LOG.info("Total Memory Accesses: " + str(self.page_table.total_memory_accesses))
        LOG.info("Total Page Faults: " + str(self.page_table.page_faults))
        LOG.info("Total Writes to Disk: " + str(self.page_table.writes_to_disk))

    def preprocess_trace(self):
        """
        Builds a dictionary with the following format: {vpn1: [index_used_1, index_used_2, ..., index_used_n],
        vpn2: ...}.
        This information should be know before starting the opt algorithm.
        None is put to an end of each vnp list to signal that this vpn won't be used again.
        :return:
        """
        trace_index_number = 0

        for elem in self.trace:
            vpn = self.page_table.get_vpn(elem[0])

            if vpn in self.time_until_use_dict:
                self.time_until_use_dict[vpn].append(trace_index_number)
            else:
                self.time_until_use_dict[vpn] = [trace_index_number]
            trace_index_number += 1

        for key in self.time_until_use_dict:
            value_list = self.time_until_use_dict[key]
            value_list.append(None)
