import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

import requests

from ..engines.common import FileWorker

logger = logging.getLogger(__name__)


class Yad2PageWorker(threading.Thread):
    HEADERS = {
        "Host": "www.yad2.co.il",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9,he;q=0.8",
        "Cookie": "SPSI=4fb48720f779bb8b8e522997063123e4; sbtsck=jav; UTGv2=h433685f4b0feae33772f7ad7586644b5d84; PHPSESSID=9l7a80r4m7aqtcje6ivce2hsk4; y2018-2-cohort=85; y2018-2-access=true; _ga=GA1.3.1207357502.1545424959; _gid=GA1.3.1621445391.1545424959; use_elastic_search=1; yad2_session=BBulquXqQ7UaWMknD05ZdD4Ie72CMZbHSWkPLz1r; fitracking_12=no; fi_utm=direct%7Cdirect%7C%7C%7C%7C; __gads=ID=58a86ba80b7c2dc3:T=1545424963:S=ALNI_MYhs8qKUhqU3xB9Ueg09FjaD-buXg; _hjIncludedInSample=1; sp_lit=fqXCzvSImMG7tXZpXwcveQ==; PRLST=Le; adOtr=84WW40bf277; favorites_userid=fbj9587662061; yad2upload=520093706.38005.0000; spcsrf=7f6b23025a40f9853eb807273025ea90"
    }
    URL_FORSALE = "http://www.yad2.co.il/api/pre-load/getFeedIndex/realestate/forsale?page={}"
    # URL_RENT = "http://www.yad2.co.il/api/pre-load/getFeedIndex/realestate/rent?page={}"

    URL_ITEM = "http://www.yad2.co.il/api/item/{id}"
    URL_ADDI_INFO = "http://www.yad2.co.il/api/item/{id}/additionalinfo"

    # URL_CONTACT_INFO = "http://www.yad2.co.il/api/item/{id}/contactinfo?id={id}"

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=True):
        super().__init__(group=group, target=target, name=name,
                         daemon=daemon)
        self.args = args
        self.kwargs = kwargs
        self.stop = False
        self.reach_end = False

        self.feed = self.kwargs.pop("feed")
        self.run()

    def run(self):
        page = self.args[0]
        try:
            page_info = self.get_page(page)
        except ValueError as e:
            logger.info("Stop reading " + str(e))
            self.reach_end = True
            return

        if isinstance(page_info, int):
            # Whoops, looks like something went wrong.
            # Try again
            page_info = self.get_page(page - 1)

        for _property in page_info:
            data = self.yad2_additions(property_id=str(_property['link_token']))
            if not isinstance(data, int):
                _property.update(data)
                self.feed[_property["id"]] = _property

    def get_page(self, page_num):
        res = requests.get(self.URL_FORSALE.format(page_num), headers=self.HEADERS)
        try:
            items = res.json()['feed']['feed_items']
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(res.text)
            return -1
        # slice items and retrieve only the values with an 'id' value
        items = [item for item in items if item.get('id')]
        logger.debug(f"New Items Retrieved: {len(items)} From page: {page_num}")

        if not len(items):
            logger.info("Stop reading pages, no more pages to read")
            raise ValueError

        return items

    def yad2_additions(self, property_id):
        res = requests.get(self.URL_ITEM.format(id=property_id), headers=self.HEADERS)
        res1 = requests.get(self.URL_ADDI_INFO.format(id=property_id), headers=self.HEADERS)
        try:
            items = res.json()
            items1 = res1.json()
            if isinstance(items, dict) and items.get("status_code") == 400:
                # in case it is an ad.. e.g. status code for id: 0rucxs, for item:
                #   {'api_version': 1, 'data': {'codeError': 5,
                #   'redirectLink': '//www.yad2.co.il/realestate/brokerage-sales/apartment-lev-motzkin,-bne-beitcha-in-kiryat-motskin?location_type=2&city=8200&neighborhood=366&HomeTypeID=1&price=500000--1',
                #   'otherData': {'catID': 2, 'subCatID': 5}}, 'status_code': 400,
                #   'error_message': 'UN_ACTIVE_STATUS', 'server_number': 98,
                #   'categoryDic': {'catEn': None, 'subCatEn': None}, 'yad1Ads': [],
                #   'agency_more_items': [], 'educational_info': [], 'pricelist_articles': [],
                #   'rating_area': []}
                # logger.info(f"status code for id: {property_id}, for item: {items}")
                return 400
        except json.JSONDecodeError as e:
            logger.warning(res.text)
            logger.warning(res1.text)
            return -1
        logger.debug(f"Retrieved additional info for property {property_id}")
        return {"info": items, "additional_info": items1}


class Yad2Crawler:
    def __init__(self, properties_per_file=1000, max_workers=8):
        self.properties_per_file = properties_per_file
        self.max_workers = max_workers
        self.more_pages = True
        self.page = 1

    def run(self):
        logger.info(f"Running Crawler.")
        feed = {}

        t = FileWorker(args=(feed,), kwargs={'properties_per_file': self.properties_per_file})
        t.start()

        executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="PageThread")
        t_list = []
        while self.more_pages:
            future = executor.submit(Yad2PageWorker, args=(self.page,), kwargs={"feed": feed})
            self.page += 1
            t_list.append(future)

            if t_list and t_list[0].done():
                t = t_list.pop(0).result()
                if t.reach_end:
                    self.more_pages = False
        executor.shutdown(wait=True)
