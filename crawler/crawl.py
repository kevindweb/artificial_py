# regex split commands
import re
# random sleep cycles
import random
# for asynchronous calls
import asyncio
# for dumping information
import json
# next two are for website crawling and processing
import bs4 as bs
import requests as req
# for getting information after a long period of time
import logging
# for getting the date and time of start time
import datetime

class TaskManager:
    '''Given multiple functions, it uses asyncio to free up complete processes and stop with callback'''
    # count variable catches running more than once
    count = 0
    done = 0
    funcs = []
    future = asyncio.Future()
    loop = asyncio.get_event_loop()

    def add_func(self, func, args):
        self.funcs.append((func, args))

    def callback(self, future):
        print("stopping loop")
        self.loop.stop()

    def set_result(self):
        self.done += 1
        if self.done == len(self.funcs):
            self.future.set_result("Done with asynchronous functions")

    def once(self):
        if self.count:
            print("Run more than once, stopping...")
            return
        elif not self.funcs:
            print("Need to add functions to manage")
            return
        # signal.signal(signal.SIGINT, self.signal_handler)
        self.count += 1
        print("Starting asyncio")
        self.future.add_done_callback(self.callback)
        for func, arg in self.funcs:
            if arg:
                asyncio.ensure_future(func(arg, self.set_result))
            else:
                asyncio.ensure_future(func(self.set_result))
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()


class Crawler:
    '''Crawler searches a websites, finds relative links, and code tags to check if content is valid python'''

    def __init__(self, websites, num):
        self.initials = [i.split(".")[0] for i in websites]
        self.urls = ['http://' + i for i in websites]
        self.file_num = num

    def handle_links(self, url, link):
        return ''.join([url, link]) if link.startswith('/') else link

    def remove_tags(self, content):
        cleanr = re.compile('<.*?>')
        # watch out for escaped characters ie &lt;
        cleantext = re.sub(cleanr, '', content)
        return cleantext

    async def get_links(self, done):
        url = self.urls[0]
        links = ["only in dev"]
        soup = bs.BeautifulSoup(req.get(self.urls[0]).text, 'html.parser')
        await asyncio.sleep(0)
        links = [i.get('href') for i in soup.body.find_all('a')]
        # links list gets handled only if link stems from original website
        print("length of links:",len(links))
        # next line filters the large list of links so that it follows this format
        # http://stackoverflow.com/questions/48434572/like-option-in-a-website-using-codeigniter
        # http://stackoverflow.com/questions/48413425/driverless-ai-cannot-import-csv-data
        links = list(set([self.handle_links(url,link) for link in links if (link and (self.initials[0] + "/questions" in link or (not "." in link and "/questions" in link and bool(re.search(r'\d', link)))))]))
        print("length of links:",len(links))
        await asyncio.sleep(random.uniform(0.1, 0.9))
        logging.info("found these urls: " + str(links))
        done()

    def find_code(self, link):
        soup = bs.BeautifulSoup(req.get(link).text, 'html.parser')
        answers = [i.contents for i in soup.body.find_all('div',{"class": "answer"})]
        # use variable answers to get the code from inside the tags and the comments as well
        print(len(code))
    # def log(self, info):
    #     if type(info) == type([]):
    #         out_file = "./json_dump" + str(self.file_num) + ".txt"
    #         print("Dumping Contents into " + out_file)
    #         data = {'links': info}
    #         with open(out_file, 'a') as outfile:
    #             outfile.write(str(data))
    #             print("things")
    #             # json.dump(data, outfile)
    #         print("JSON dumped")
    #     else:
    #         info = "\nfile_dump " + str(self.file_num) + "\n\n" + info
    #         with open(self.log_file, 'a') as outfile:
    #             outfile.write(info)
    #         print("Information logged")

if __name__ == "__main__":
    now = datetime.datetime.now()
    outfile = "./log/out_file(" + now.strftime("%m-%d__%H:%M") + ").txt"
    # logging.basicConfig(filename=outfile, level=logging.DEBUG)
    c = Crawler(["stackoverflow.com"], 1)
    # m = TaskManager()
    # m.add_func(c.get_links, False)
    # m.once()
    c.find_code("https://stackoverflow.com/questions/9257094/how-to-change-a-string-into-uppercase")
