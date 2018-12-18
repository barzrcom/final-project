import sys

import json
import logging
import os
import re
import requests
import threading

logger = logging.getLogger(__name__)


class FileWorker(threading.Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=True):
        super().__init__(group=group, target=target, name=name,
                         daemon=daemon)
        self.args = args
        self.kwargs = kwargs
        self.stop = False

        self.properties_per_page = self.kwargs.pop("properties_per_page")

    @staticmethod
    def gen_file(feeds):
        f_name = "feeds_1.json"
        while os.path.exists(f_name):
            num = re.match(r".+_([\d]+).+", f_name).group(1)
            f_name = f_name.replace(num, str(int(num) + 1))

        logger.info(f"Creating new file: {f_name}.")
        with open(f_name, "a") as f:
            json.dump(feeds, f, ensure_ascii=False)

    def run(self):
        logger.info("FileWorker is waiting for enough jobs to dump to file..")
        feed = self.args[0]
        while not self.stop:
            while len(feed) > self.properties_per_page:
                keys = list(feed.keys())[:self.properties_per_page]
                dump = {k: feed.pop(k) for k in keys}
                # when gets to the number of page that the user wants, dump current feed to file
                self.gen_file(dump)
        if feed:
            # dump all feeds that left. properly less than "self.properties_per_page"
            self.gen_file(feed)


class PageWorker(threading.Thread):
    HEADERS = {
        "Host": "www.yad2.co.il",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9,he;q=0.8",
        "Cookie": "y2018-2-cohort=90; y2018-2-access=true; use_elastic_search=1; _ga=GA1.3.238762837.1544441703; _gid=GA1.3.1497888994.1544441703; PHPSESSID=3a4daf84ad73028868fc36a651c74c46; fitracking_12=no; __gads=ID=9839c78fc20ffef1:T=1544441656:S=ALNI_MYXGPpuyPojVD4RM4_G4GyrK1bk4w; TS011ed9fa=01cdef7ca22ba61476b4cd131f1629d7d806861c1ffddf352a867b0f521ca618f633a58786bec7bbca11f81b0692a0cbf3dad33405054d9206da74d43c06de954c028b892311864321aa9b6ca652700da35b0177d3; SPSI=146c1ae28ca53f4374aaeaccef952d90; sbtsck=jav; UTGv2=h4bc5bcf4bdd24a24ccdf8ffc82301382c29; yad2_session=3HqzL7EtMaR8Khl49Xn39DSsHc9KO3Bm8mpV3u6P; fi_utm=direct%7Cdirect%7C%7C%7C%7C; PRLST=PL; favorites_userid=chi6410618182; adOtr=1c4a126Beac; historyprimaryarea=sharon_area; historysecondaryarea=raanana_kfar_saba; yad2upload=520093706.38005.0000; BetterJsPop0=1; y1-site=_in_x1_b_285_s_nad_pop_1rashy_rotemshany; spcsrf=ed41e68e84df220c7c617231be6e46df"
    }
    URL_FORSALE = "http://www.yad2.co.il/api/pre-load/getFeedIndex/realestate/forsale?page={}"

    URL_ITEM = "http://www.yad2.co.il/api/item/{id}"
    URL_ADDI_INFO = "http://www.yad2.co.il/api/item/{id}/additionalinfo"

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=True):
        super().__init__(group=group, target=target, name=name,
                         daemon=daemon)
        self.args = args
        self.kwargs = kwargs
        self.stop = False
        self.reach_end = False

        self.feed = self.kwargs.pop("feed")

    def run(self):
        page = self.args[0]
        try:
            page_info = self.get_page(page)
        except ValueError:
            logger.info("Stop reading")
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
        except json.JSONDecodeError as e:
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


class Crawler:
    def __init__(self, properties_per_page=1000, max_workers=8):
        self.properties_per_page = properties_per_page
        self.max_workers = max_workers
        self.more_pages = True
        self.page = 1

    def run(self):
        logger.info(f"Running Crawler.")
        feed = {}

        t = FileWorker(args=(feed,), kwargs={'properties_per_page': self.properties_per_page})
        t.start()

        while self.more_pages:
            t_list = []
            for number in range(self.max_workers):
                t = PageWorker(args=(self.page,), kwargs={"feed": feed})
                t.start()
                t_list.append(t)
                self.page += 1

            [t.join() for t in t_list]
            if any([t.reach_end for t in t_list]):
                self.more_pages = False
                t.stop = True
                t.join()
                break


if __name__ == '__main__':
    c_handler = logging.StreamHandler(sys.stdout)
    c_format = logging.Formatter('%(asctime)s [ %(funcName)-15s] %(levelname)s: (%(threadName)-10s) %(message)s')
    c_handler.setFormatter(c_format)
    logger.setLevel(level=logging.INFO)
    logger.addHandler(c_handler)

    c = Crawler()
    c.run()
