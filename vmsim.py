"""
VM Simulator for Page Replacement Algorithms

Usage:  python vmsim.py -n <numframes> -a <opt|clock|aging|lru> [-r <refresh>] <tracefile>
"""
import argparse
import datetime
import logging
import sys

import algorithms.aging as aging
import algorithms.clock as clock
import algorithms.lru as lru
import algorithms.opt as opt
import input_parser as iparser
import page_table as pt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--numframes", default=8, help="numframes")
    parser.add_argument("--refresh", default=5, help="refresh time in ms (for aging alg): <refresh>")
    parser.add_argument("--tracefile", default="./gcc.trace", help="tracefile (optional): <tracefile>")
    args = parser.parse_args()

    cmd_line_args = list()
    cmd_line_args.append(args.numframes)
    cmd_line_args.append(args.refresh) if args.refresh else cmd_line_args.append(None)
    cmd_line_args.append(args.tracefile)

    logger.info("Parsed args: %s", cmd_line_args)

    num_frames = int(cmd_line_args[0])
    refresh = float(cmd_line_args[1])
    trace_file = cmd_line_args[2]

    memory_addresses = iparser.parse_trace_file(trace_file)
    if not memory_addresses:
        logger.error("Trace file parsing error. Terminating.")
        sys.exit(0)

    # build the model for our page table, 32bit address space, initialize the table
    page_table = pt.PageTable(num_frames)
    algorithms = (opt.Opt, clock.Clock, aging.Aging, lru.LRU)
    results = []

    for alg_name in algorithms:
        if not alg_name == 'Aging':
            alg = (page_table, memory_addresses)
        else:
            alg = aging.Aging(page_table, memory_addresses, refresh)
        t_0 = datetime.datetime.now()
        result_tuple = alg.run_algorithm()
        t_1 = datetime.datetime.now()
        total = t_1 - t_0
        results.append(result_tuple.get_result(alg_name, trace_file, total))
        logger.info("TOTAL %s TIME: %s", alg_name, str(total))


if __name__ == "__main__":
    logging.basicConfig(level=logging.NOTSET)
    # logging.disable(logging.INFO)
    logger = logging.getLogger(__name__)

    main()
