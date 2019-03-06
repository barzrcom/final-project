import sys

import argparse
import logging

from .workers import Crawler

logger = logging.getLogger(__name__.split(".")[0])


def main(args):
    parser = argparse.ArgumentParser(description="Yad2 Crawler Program")
    parser.add_argument("-p", "--properties_per_file", type=int, default=1000, required=False,
                        help="Set how many properties to collect for each file.")
    parser.add_argument("-m", "--max_workers", type=int, default=15, required=False,
                        help="Program threads number.")
    args = parser.parse_args(args)

    c_handler = logging.StreamHandler(sys.stdout)
    c_format = logging.Formatter('%(asctime)s [ %(funcName)-15s] %(levelname)s: (%(threadName)-10s) %(message)s')
    c_handler.setFormatter(c_format)
    logger.setLevel(level=logging.DEBUG)
    logger.addHandler(c_handler)

    c = Crawler(args.properties_per_file, args.max_workers)
    c.run()
