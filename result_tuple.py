class ResultTuple:

    def __init__(self, frames, total_mem_access, page_faults, writes, refresh_rate):
        self.frames = frames
        self.total_mem_access = total_mem_access
        self.page_faults = page_faults
        self.writes = writes
        self.refresh = refresh_rate

    def get_result(self, alg, trace_file, total_time):
        return (alg,
                trace_file,
                self.frames,
                self.total_mem_access,
                self.page_faults,
                self.writes,
                self.refresh,
                total_time)

    # alg,trace_file,frames,total_mem_access,page_faults,writes,refresh,total_time
    # (frames, total_mem_access, page_faults, writes)
    # (len(self.page_table.frame_table), self.page_table.total_memory_accesses,self.page_table.page_faults, self.page_table.writes_to_disk)
    # (3, 10, 8, 3)
