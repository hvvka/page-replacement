# Assumptions:
# 4kb pages
# 32 bit address space
#
# This means there are 2^12 bits, or bottom 12 bits of the addresses reserved for
# intra-page addressing. The rest determine if we are using a page that's already in use
# So we're looking at the first 20 bits to see if we've got a match.

import circular_queue as cq
from algorithms.aging import Aging


class PageTable:

    def __init__(self, how_many_frames):
        """
        :param how_many_frames: total amount of frames in page table
        """
        self.num_frames = how_many_frames
        self.page_faults = 0
        self.writes_to_disk = 0
        self.total_memory_accesses = 0

        self.frame_table = list()

        for _ in range(0, self.num_frames):
            next_frame = Frame()
            next_frame.dirty = False
            next_frame.in_use = False
            self.frame_table.append(next_frame)

        # dictionary enhancing OPT algorithm mapping VPN to PPN
        self.fast_index = dict()

        # used in clock algorithm
        self.frame_queue = cq.CircularQueue(self.num_frames)

    @staticmethod
    def get_vpn(memory_address):
        """
        Computes Virtual Page Number from given memory address
        :param
        :return:
        """
        # 000 is page offset
        vpn_mask = 0xFFFFF000
        hex_int = int(memory_address, 16)
        vpn_value = hex_int & vpn_mask
        return vpn_value >> 12


class Frame:
    def __init__(self):
        # virtual page number
        self.vpn = 0
        # physical page number
        self.ppn = 0
        # dirty (D) bit (modified)
        self.dirty = False
        # "used" bit/reference bit
        self.in_use = False

        # how many instructions until this page is next used (OPT only)
        self.instructions_until_next_reference = None
        # reference bit used by AGING algorithm
        self.reference = False
        # aging value used by AGING algorithm
        self.aging_value = 0
        # last reference used by LRU algorithm
        self.last_reference = 0

    def __repr__(self):
        return "vpn:\t{}\tppn:\t{}\tdirty:\t{}\tin_use:\t{}\tinstr_until_next_ref:\t{}\treference:\t{}\taging_value:\t{}\tlast_reference\t{}\t".format(
            self.vpn, self.ppn, self.dirty, self.in_use, self.instructions_until_next_reference, self.reference,
            format(self.aging_value, '#0' + str(Aging.COUNTER_LENGTH + 2) + 'b'), self.last_reference)
