"""
VM Simulator for Page Replacement Algorithms

Usage:  python vmsim.py -n <numframes> -a <opt|clock|aging|lru> [-r <refresh>] <tracefile>
"""
import argparse
import copy
import csv
import datetime
import logging
import sys

import algorithms.aging as aging
import algorithms.clock as clock
import algorithms.lru as lru
import algorithms.opt as opt
import input_parser as iparser
import page_table as pt

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


def serialize_results(results, output_file):
    with open(output_file, "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(
            ('alg', 'trace_file', 'frames', 'total_mem_access', 'page_faults', 'writes', 'refresh', 'total_time'))
        writer.writerows(results)


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
        results.append(result_tuple.get_result(alg.__str__(), trace_file, total_time))
        LOG.info("TOTAL %s TIME: %s ms", alg.__str__(), str(total_time))

    output_file = 'results/' + str(num_frames) + '_frames.csv'
    serialize_results(results, output_file)


if __name__ == "__main__":
    main()
