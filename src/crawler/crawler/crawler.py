import sys

import argparse
import logging

from .engines.yad2 import Yad2Crawler
from .engines.homeprice import HomePriceCrawler

logger = logging.getLogger(__name__.split(".")[0])


def main(args):
    parser = argparse.ArgumentParser(description="Yad2 Crawler Program")
    parser.add_argument("-p", "--properties_per_file", type=int, default=1000, required=False,
                        help="Set how many properties to collect for each file.")
    parser.add_argument("-e", "--engine", type=str, default="yad2", required=False,
                        help="Run crawler on given engine.")
    parser.add_argument("-m", "--max_workers", type=int, default=15, required=False,
                        help="Program threads number.")
    args = parser.parse_args(args)

    c_handler = logging.StreamHandler(sys.stdout)
    c_format = logging.Formatter('%(asctime)s [ %(funcName)-15s] %(levelname)s: (%(threadName)-10s) %(message)s')
    c_handler.setFormatter(c_format)
    logger.setLevel(level=logging.INFO)
    logger.addHandler(c_handler)

    if args.engine == 'yad2':
        c = Yad2Crawler(args.properties_per_file, args.max_workers)
    elif args.engine == 'homeprices':
        c = HomePriceCrawler(args.properties_per_file * 10, args.max_workers)
    else:
        raise ValueError(f"Unknown value for engine: {args.engine}")

    c.run()
