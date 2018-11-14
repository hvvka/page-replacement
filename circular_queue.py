"""
Circular queue implementation for use in the clock algorithm
"""
import page_table as pt


class CircularQueue:
    """
    Circular queue structure that takes initial size as parameter
    """

    def __init__(self, queue_size):
        """
        Must be a queue of frames
        :param queue_size: initial queue size
        """
        self.qsize = queue_size
        self.pointer = 0
        self.list = []
        for i in range(0, queue_size):
            self.list.append(pt.Frame())
            self.list[i].ppn = i

    def add_or_update_successful(self, vpn, read_or_write):
        """
        :param vpn: a frame to be added to the queue
        :param read_or_write: specifies memory access mode
        :return: False if a frame was NOT added, because the queue is full (will be page fault)
                 True otherwise
        """
        # set sentinel value
        added = False

        # iterate through the list and try to add
        for elem in self.list:
            # if we have an element NOT in use, then we can add there
            # also need to check if we're just doing an update
            if not elem.in_use or elem.vpn == vpn:
                added = True
                elem.in_use = True
                elem.vpn = vpn
                # if we're doing a write, need to set dirty bit
                elem.dirty = read_or_write == 'W'
                # if we're not writing, then we're reading, and so we need to set the reference bit
                elem.reference = read_or_write != 'W'

                return added

        return added

    def remove(self, ppn):
        """
        Removes page from queue
        :param ppn: the victim page
        """
        removal_page = self.list[ppn]
        removal_page.in_use = False
        removal_page.referenced = False
        removal_page.dirty = False
        removal_page.vpn = None

    def find_victim(self):
        """
        Get a victim page
        :return: victim frame
        """
        for _ in range(0, self.qsize):
            elem = self.list[self.pointer]
            # if we find a page which is unreferenced (recently) and clean, that's our victim
            if not elem.reference and not elem.dirty:
                # return it's PPN, so we can index into it and remove it
                return elem.ppn

            if elem.reference:
                elem.reference = False

            # use modulus of queue size to achieve a circular queue
            self.pointer = (self.pointer + 1) % self.qsize
            assert self.pointer <= self.qsize

        # if we get this far, no victim page was found,
        # need to flush __dirty unreferenced pages__ to disk
        # and then repeat

        return None

    def flush_dirty_and_unreferenced_pages(self):
        """
        Runs the swap daemon
        NOTE: need to account for a DISK WRITE in clock algorithm
        :return: the number of removed pages/disk writes
        """
        number_of_disk_writes = 0
        for elem in self.list:
            if elem.dirty and not elem.reference:
                elem.dirty = False
                number_of_disk_writes += 1

        return number_of_disk_writes
