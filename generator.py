"""
Trace file generator.
"""

import argparse
import os
import random

OUTPUT_DIRECTORY = 'data/'


class Generator:
    """
    Generates random output file representing memory for given number of pages.
    """
    def __init__(self, pages: int):
        self.pages = pages

    def generate(self):
        """
        Generates output file `<number of pages>.trace` in `data` directory.
        """
        self.create_data_dir()
        filename: str = OUTPUT_DIRECTORY + str(self.pages) + '.trace'
        with open(filename, 'w+') as file:
            for _ in range(self.pages):
                file.write(RandomPage().__repr__())

    @staticmethod
    def create_data_dir():
        """
        Creates directory `data` in project root.
        """
        if not os.path.exists(OUTPUT_DIRECTORY):
            os.makedirs(OUTPUT_DIRECTORY)


VPN_UPPER_BOUND = 150  # max: 20**2-1 = 399
READ_PROBABILITY = 75  # in %


class RandomPage:
    """
    Representation of page in memory consisting of random page address and read or write access.
    """

    def __init__(self):
        self.vpn = '{:05x}'.format(random.randint(0, VPN_UPPER_BOUND))
        self.ppn = '{:03x}'.format(random.getrandbits(12))
        self.r_w = 'W' if random.randint(0, 100) > READ_PROBABILITY else 'R'

    def __repr__(self):
        return self.vpn + self.ppn + ' ' + self.r_w + '\n'


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
