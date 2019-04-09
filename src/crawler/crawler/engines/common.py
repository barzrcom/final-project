import json
import logging
import os
import re
import threading

logger = logging.getLogger(__name__)


class FileWorker(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=True):
        super().__init__(group=group, target=target, name=name, daemon=daemon)
        self.args = args
        self.kwargs = kwargs
        self.stop = False

        self.properties_per_file = self.kwargs.pop("properties_per_file")
        self.file_format = self.kwargs.get("file_format", "feeds_1.json")

    def gen_file(self, feeds):
        f_name = self.file_format
        while os.path.exists(f_name):
            num = re.match(r".+_([\d]+).+", f_name).group(1)
            f_name = f_name.replace(num, str(int(num) + 1))

        logger.info(f"Creating new file: {f_name}.")
        with open(f_name, "a", encoding='utf8') as f:
            json.dump(feeds, f, ensure_ascii=False)

    def run(self):
        logger.info("FileWorker is waiting for enough jobs to dump to file..")
        feed = self.args[0]
        while not self.stop:
            while len(feed) > self.properties_per_file:
                if isinstance(feed, dict):
                    keys = list(feed.keys())[:self.properties_per_file]
                    dump = {k: feed.pop(k) for k in keys}
                elif isinstance(feed, list):
                    keys = feed[:self.properties_per_file]
                    dump = [feed.pop(0) for k in keys]
                # when gets to the number of page that the user wants, dump current feed to file
                self.gen_file(dump)
        if feed:
            # dump all feeds that left. properly less than "self.properties_per_file"
            self.gen_file(feed)
