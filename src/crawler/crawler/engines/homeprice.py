import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode

import requests

from ..engines.common import FileWorker
from ..utils import init_server

logger = logging.getLogger(__name__)


class HomePricePageWorker(threading.Thread):
    HEADERS = {
        "Host": "homeprices.yad2.co.il",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9,he;q=0.8",
        "Cookie": "SPSI=4fb48720f779bb8b8e522997063123e4; sbtsck=jav; UTGv2=h433685f4b0feae33772f7ad7586644b5d84; PHPSESSID=9l7a80r4m7aqtcje6ivce2hsk4; y2018-2-cohort=85; y2018-2-access=true; _ga=GA1.3.1207357502.1545424959; _gid=GA1.3.1621445391.1545424959; use_elastic_search=1; yad2_session=BBulquXqQ7UaWMknD05ZdD4Ie72CMZbHSWkPLz1r; fitracking_12=no; fi_utm=direct%7Cdirect%7C%7C%7C%7C; __gads=ID=58a86ba80b7c2dc3:T=1545424963:S=ALNI_MYhs8qKUhqU3xB9Ueg09FjaD-buXg; _hjIncludedInSample=1; sp_lit=fqXCzvSImMG7tXZpXwcveQ==; PRLST=Le; adOtr=84WW40bf277; favorites_userid=fbj9587662061; yad2upload=520093706.38005.0000; spcsrf=7f6b23025a40f9853eb807273025ea90",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    URL_DEALS = "http://homeprices.yad2.co.il/ajax/taxdeals.php"

    DATA = {
        "json[page_num]": 1,
        "json[max]": 100,
        "json[controller]": "street",
        "json[page]": "street",
        "json[city]": "",
        "json[street]": "",
        "json[housenum": "",
        "json[IsGindi]": 0,
        "json[filter][0][Name]": "rooms",
        "json[filter][0][Type]": "slider",
        "json[filter][0][data][Min]": 1,
        "json[filter][0][data][Max]": 10,
        "json[filter][1][Name]": "square_meters",
        "json[filter][1][Type]": "slider",
        "json[filter][1][data][Min]": 10,
        "json[filter][1][data][Max]": 1000,
        "json[filter][2][Name]": "date",
        "json[filter][2][Type]": "select",
        "json[filter][2][data][month]": "",
        "json[filter][2][data][year]": "",
        "json[filter][3][Name]": "price",
        "json[filter][3][Type]": "input",
        "json[filter][3][data][from]": "",
        "json[filter][3][data][until]": "",
        "json[filter][4][Name]": "new_aprt",
        "json[filter][4][Type]": "checkbox",
        "json[filter][4][data][checked]": "false",
        "json[filter][5][Name]": "yad2_deals",
        "json[filter][5][Type]": "checkbox",
        "json[filter][5][data][checked]": False
    }

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=True):
        super().__init__(group=group, target=target, name=name, daemon=daemon)
        self.args = args
        self.kwargs = kwargs
        self.stop = False
        self.reach_end = False

        self.feed = self.kwargs.pop("feed")
        self.run()

    def run(self):
        city, street, *arg = self.args
        try:
            _properties = self.get_data_from_info(city, street)
        except Exception as e:
            logger.error(e)
            raise
        self.feed.extend(_properties)

    def get_data_from_info(self, city, street):
        res = []
        page = 1
        data = self.DATA
        data["json[page_num]"] = 1

        data["json[city]"] = city
        data["json[street]"] = street
        logger.debug(data["json[city]"])
        logger.debug(data["json[street]"])

        bla = requests.post(self.URL_DEALS, headers=self.HEADERS, data=urlencode(data), timeout=10)

        deals = bla.json()
        logger.debug(len(deals["Results"]))
        for deal in deals.get("Results", []):
            deal["line"]["city"] = city
            res.append(deal['line'])
        page += 1

        while page < int(deals.get('MaxPage', 0)) + 1:
            data["json[page_num]"] = page
            bla = requests.post(self.URL_DEALS, headers=self.HEADERS, data=urlencode(data), timeout=10)
            deals = bla.json()
            logger.debug(len(deals["Results"]))
            for deal in deals["Results"]:
                deal["line"]["city"] = city
                res.append(deal['line'])
            page += 1
        return res


class HomePriceCrawler:
    def __init__(self, properties_per_file=10000, max_workers=8, db_name="yad2_test_1", col="col1"):
        self.properties_per_file = properties_per_file
        self.max_workers = max_workers
        self.more_pages = True

        db, collection = init_server(db_name=db_name, col=col)

        res = collection.find({}, {"city": 1, "street": 1})

        res = {v['city'] + v['street']: v for v in res if v['city'] and v['street']}.values()

        self.data = [(v['city'], v['street']) for v in res]

    def run(self):
        logger.info(f"Running Crawler.")
        feed = []

        t = FileWorker(args=(feed,), kwargs={'properties_per_file': self.properties_per_file,
                                             'file_format': "homeprice_1.json"})
        t.start()

        executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="PageThread")
        t_list = []
        # print([val for val in self.data])
        for city, street in self.data:
            # TODO: add neighborhood to each item
            future = executor.submit(HomePricePageWorker, args=(city, street), kwargs={"feed": feed})
            t_list.append(future)

        t_list[-1].result()

        logger.info("finish")
        executor.shutdown(wait=True)
