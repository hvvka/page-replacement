"""
Routine for parsing input from provided .trace files
"""

import logging
import os
import sys

LOGGER = logging.getLogger(__name__)


def parse_trace_file(file_path):
    """
    Method to parse trace files
    :param file_path: a string representing the relative file path to our trace in the filesystem
    :return: a list of tuples, in this format: [(MEM, R/W),(MEM, R/W), ... ]
    """

    if not os.path.isfile(file_path):
        LOGGER.error("Trace file '%s' doesn't exist.", file_path)
        return None

    try:
        with open(file_path, "r", newline="\n") as f:
            data_points = f.readlines()
    except IOError:
        LOGGER.error("Exception while reading trace file '%s'. Terminating.", file_path)
        sys.exit(0)

    data_point_tuple_list = []
    for value in range(0, len(data_points)):
        split_string = data_points[value].split(" ")

        memory_address = split_string[0].strip()
        read_or_write = split_string[1].strip()

        current_tuple = (memory_address, read_or_write)
        data_point_tuple_list.append(current_tuple)

    return data_point_tuple_list


def hex_string_to_binary_int(hex_string):
    hex_string_to_decimal_int = int(hex_string, 16)
    binary_int = bin(hex_string_to_decimal_int)
    return binary_int
