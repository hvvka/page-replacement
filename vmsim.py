"""
VM Simulator for Page Replacement Algorithms

Usage:  python vmsim.py -n <numframes> -a <opt|clock|aging|lru> [-r <refresh>] <tracefile>
"""
import argparse
import copy
import csv
import datetime
import logging
import os
import sys

import algorithms.aging as aging
import algorithms.clock as clock
import algorithms.lru as lru
import algorithms.opt as opt
import input_parser as iparser
import page_table as pt

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

RESULT_DIR = 'results/'


def serialize_results(results, output_file: str):
    """
    Writes algorithm results to CSV file.
    :param results: an array of result tuples
    :param output_file: path to output file
    """
    with open(output_file, "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(
            ('alg', 'trace_file', 'frames', 'total_mem_access', 'page_faults', 'writes', 'refresh', 'total_time'))
        writer.writerows(results)


def create_results_dir(trace_file, num_frames: int) -> str:
    """
    Creates (if doesn't exist) and returns path to write results.
    :param trace_file: path to generated trace file
    :param num_frames: number of frames that were used to perform algorithm
    :return: output directory path to write results
    """
    output_path: str = RESULT_DIR + os.path.splitext(os.path.basename(trace_file))[0] + '_trace/'
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    return output_path + str(num_frames) + '_frames.csv'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--numframes", default=3, help="numframes")
    parser.add_argument("--refresh", default=5, help="refresh time [ms] (for aging alg): <refresh>")
    parser.add_argument("--tracefile", default="tests/resources/test.trace", help="tracefile (optional): <tracefile>")
    args = parser.parse_args()

    cmd_line_args = list()
    cmd_line_args.append(args.numframes)
    cmd_line_args.append(args.refresh) if args.refresh else cmd_line_args.append(None)
    cmd_line_args.append(args.tracefile)

    LOG.info("Parsed args: %s", cmd_line_args)

    num_frames = int(cmd_line_args[0])
    refresh = float(cmd_line_args[1])
    trace_file = cmd_line_args[2]

    memory_addresses = iparser.parse_trace_file(trace_file)
    if not memory_addresses:
        LOG.error("Trace file parsing error. Terminating.")
        sys.exit(0)

    # build the model for our page table, 32bit address space, initialize the table
    algorithms = (clock.Clock, lru.LRU, aging.Aging, opt.Opt)
    results = []

    for algorithm in algorithms:
        page_table = pt.PageTable(num_frames)
        if not algorithm == aging.Aging:
            alg = algorithm(page_table, copy.copy(memory_addresses))
        else:
            alg = algorithm(page_table, copy.copy(memory_addresses), refresh)
        t_0 = datetime.datetime.now()
        result_tuple = alg.run_algorithm()
        t_1 = datetime.datetime.now()
        LOG.info(vars(result_tuple))
        total_time = (t_1 - t_0).total_seconds() * 1000
        results.append(result_tuple.get_result(alg.__str__(), os.path.basename(trace_file), total_time))
        LOG.info("TOTAL %s TIME: %s ms", alg.__str__(), str(total_time))

    output_file = create_results_dir(trace_file, num_frames)
    serialize_results(results, output_file)

if __name__ == "__main__":
    main()
