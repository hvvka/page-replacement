"""
Trace file generator.
"""

import argparse
import random


class Generator:
    """
    Generates random output file representing memory for given number of pages.
    """

    def __init__(self, pages: int):
        self.pages = pages

    def generate(self):
        """
        Generates output file `<number of pages>.trace` in `data` directory (must exist!).
        """
        filename: str = 'data/' + str(self.pages) + '.trace'
        with open(filename, 'w+') as file:
            for _ in range(self.pages):
                file.write(RandomPage().__repr__())


PPN_UPPER_BOUND = 2
READ_PROBABILITY = 75  # in %


class RandomPage:
    """
    Representation of page in memory consisting of random page address and read or write access.
    """

    def __init__(self):
        self.ppn = ''.join([str(random.randint(0, PPN_UPPER_BOUND)) for _ in range(5)])
        self.vpn = '{:03x}'.format(random.getrandbits(12))
        self.r_w = 'W' if random.randint(0, 100) > READ_PROBABILITY else 'R'

    def __repr__(self):
        return self.ppn + self.vpn + ' ' + self.r_w + '\n'


def main():
    """
    Allows to invoke generator from CLI and passing file size by `--pages <number>` argument.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", default=250000, help="number of pages (output file size in lines)")
    args = parser.parse_args()
    Generator(int(args.pages)).generate()


if __name__ == "__main__":
    main()
