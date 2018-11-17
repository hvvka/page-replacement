"""
Provides output data structure for algorithms.
"""


class ResultTuple:
    """
    Single line of results of any algorithm.
    """

    def __init__(self, frames: int, total_mem_access: int, page_faults: int, writes: int, refresh_rate):
        self.frames = frames
        self.total_mem_access = total_mem_access
        self.page_faults = page_faults
        self.writes = writes
        self.refresh = refresh_rate

    def get_result(self, alg: str, trace_file: str, total_time):
        """
        Adds additional (general) parameters to the result tuple.
        :param alg: algorithm name
        :param trace_file: name of file that was used as data source
        :param total_time: total algorithm execution time in miliseconds
        :return: a line to be written into CSV
        """
        return (alg,
                trace_file,
                self.frames,
                self.total_mem_access,
                self.page_faults,
                self.writes,
                self.refresh,
                total_time)
