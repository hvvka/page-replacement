# Thoughts:  We have 4kb pages, and a 32 bit address space.
#            This means we have 2^12 bits, or bottom 12 bits of our addresses reserved for
#            intra-page addressing. The rest determine if we are using a page that's already in use
#            So we're looking at the first 20 bits to see fi we've got a match...
import circular_queue as cq


class PageTable:

    def __init__(self, how_many_frames):
        """
        next_free_frame - use this to make added a frame and checking for page fault O(1)
        frame_queue - circular queue of frames, used ONLY in the CLOCK algorithm
        :param how_many_frames: total amount of frames
        """
        self.num_frames = how_many_frames
        self.page_faults = 0
        self.writes_to_disk = 0
        self.total_memory_accesses = 0
        self.next_free_frame = 0
        self.fast_index = dict()

        self.frame_table = list()

        self.frame_queue = cq.CircularQueue(self.num_frames)

        for frame in range(0, self.num_frames):
            next_frame = Frame()
            next_frame.dirty = False
            next_frame.in_use = False
            self.frame_table.append(next_frame)

    def get_pte(self, memory_tuple):
        """
        Translates memory address into a VPN and an OFFSET
        :param memory_tuple: tuple from trace file containing memory address and r/w bit
        """
        mem_addr = memory_tuple[0]
        rw_bit = memory_tuple[1]

        vpn = self.get_vpn(mem_addr)
        offset = self.get_page_offset(mem_addr)

    @staticmethod
    def get_vpn(memory_address):
        """
        vpn_mask - 0xFFFFF000  # 0b11111111111111111111000000000000 mask first 20 bits 0xFFFFF0000
        :param memory_address: memory address
        :return: vpn_value
        """
        vpn_mask = 0xFFFFF000
        hex_int = int(memory_address, 16)
        vpn_value = hex_int & vpn_mask
        return vpn_value

    @staticmethod
    def get_page_offset(memory_address):
        """
        page_offset_mask - 0b00000000000000000000111111111111 mask bottom 12 bits  0x00000FFFF
        :param memory_address: memory address
        :return: offset_value
        """
        page_offset_mask = 0x00000FFF
        hex_int = int(memory_address, 16)
        offset_value = hex_int & page_offset_mask
        return offset_value


class Frame:
    def __init__(self):
        """
        VPN - Virtual Page Number
        dirty - D bit
        in_user - R bit
        PPN - Physical Page Number
        instructions_until_next_reference - how many instructions until this page is next used

        reference - reference bit used by CLOCK algorithm
        aging_value - aging value used by AGING algorithm
        last_referenced - last referenced used by LRU algorithm
        """
        self.VPN = 0
        self.dirty = False
        self.in_use = False
        self.PPN = 0
        self.instructions_until_next_reference = None

        self.reference = False
        self.aging_value = 0
        self.last_reference = 0


class VirtualAddress:
    def __init__(self, address):
        """
        virtual_page_number - top 20 bits
        page_offset - bottom 12 bits
        """
        self.virtual_page_number = None
        self.page_offset = None
