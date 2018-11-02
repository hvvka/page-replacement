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
    parser.add_argument("--algorithm", default="opt", help="algorithm: <opt|clock|aging|lru>")
    parser.add_argument("--refresh", default=5, help="refresh time in ms (for aging alg): <refresh>")
    parser.add_argument("--tracefile", default="./gcc.trace", help="tracefile (optional): <tracefile>")
    args = parser.parse_args()

    cmd_line_args = list()
    cmd_line_args.append(args.numframes)
    cmd_line_args.append(args.algorithm)
    cmd_line_args.append(args.refresh) if args.refresh else cmd_line_args.append(None)
    cmd_line_args.append(args.tracefile)

    logger.info("Parsed args: {}".format(cmd_line_args))

    num_frames = int(cmd_line_args[0])

    algorithm = cmd_line_args[1]

    refresh = float(cmd_line_args[2])
    trace_file = cmd_line_args[3]

    memory_addresses = iparser.parse_trace_file(trace_file)
    if not memory_addresses:
        logger.error("Trace file parsing error. Terminating.")
        sys.exit(0)

    # build the model for our page table, 32bit address space, initialize the table
    page_table = pt.PageTable(num_frames)

    if algorithm == "opt":
        opt_alg = opt.Opt(page_table, memory_addresses)
        t0 = datetime.datetime.now()
        opt_alg.run_algorithm()
        t1 = datetime.datetime.now()
        total = t1 - t0
        logger.info("TOTAL RUNNING TIME: " + str(total))

    elif algorithm == "clock":
        clock_algorithm = clock.Clock(page_table, memory_addresses)
        t0 = datetime.datetime.now()
        clock_algorithm.run_algorithm()
        t1 = datetime.datetime.now()
        total = t1 - t0
        logger.info("TOTAL RUNNING TIME: " + str(total))

    elif algorithm == "aging":
        aging_algorithm = aging.Aging(page_table, memory_addresses, refresh)
        t0 = datetime.datetime.now()
        aging_algorithm.run_algorithm()
        t1 = datetime.datetime.now()
        total = t1 - t0
        logger.info("TOTAL RUNNING TIME: " + str(total))

    elif algorithm == "lru":
        LRU_algorithm = lru.LRU(page_table, memory_addresses)
        t0 = datetime.datetime.now()
        LRU_algorithm.run_algorithm()
        t1 = datetime.datetime.now()
        total = t1 - t0
        logger.info("TOTAL RUNNING TIME: " + str(total))

    else:
        logger.warning("Invalid algorithm name. Acceptable choices are: opt, clock, aging, lru.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.NOTSET)
    # logging.disable(logging.INFO)
    logger = logging.getLogger(__name__)

    main()
