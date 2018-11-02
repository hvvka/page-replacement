""" Routine for parsing input from provided .trace files
"""

import logging
import os

logger = logging.getLogger(__name__)


def parse_trace_file(file_path):
    """ Method to parse trace files
    :param file_path: a string representing the relative file path to our trace in the filesystem
    :return: a list of tuples, in this format: [(MEM_ADRR, R/W), ... ]
    """

    if not os.path.isfile(file_path):
        logger.error("Trace file doesn't exist")
        return None


    data_points = []
    with open(file_path, "r", newline="\n") as f:
        data_points = f.readlines()

    # iterate through our data points list and split all of our data points
    # into a tuple with this format: (MEMORY_ADDRESS, R/W),
    # store all of these in a lit of tuples [(MEM, R/W),(MEM, R/W), ... ]
    data_point_tuple_list = []
    for value in range(0, len(data_points)):
        # Split each data point int a string on the space (" ")
        # between its address and R/W
        split_string = data_points[value].split(" ")

        # store mem address and r/w in local variables
        memory_address = split_string[0].strip()
        read_or_write = split_string[1].strip()

        # add our local variables to the tuple list
        current_tuple = (memory_address, read_or_write)
        data_point_tuple_list.append(current_tuple)

    return data_point_tuple_list


def hex_string_to_binary_int(hex_string):
    """ Method that takes a hexadecimal number encoded as a string,
        and outputs that same number as a binary int
    :param hex_string: a string representing a hex number
    :return: that same hex number, encoded as a binary int
    """
    hex_string_to_decimal_int = int(hex_string, 16)
    binary_int = bin(hex_string_to_decimal_int)
    return binary_int
