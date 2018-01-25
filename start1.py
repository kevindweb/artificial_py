# for system commands
import os
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


def run_next_file(contents, num):
    file = "./start" + str(num) + ".py"
    # process replicates, increasing the file number
    fh = open(file, type)
    fh.write(contents)
    # call the next process to run and quit after process done
    # os.system("python " + file)
    # quit()


def split_by_func(contents):
    # gets all the names and locations of functions in its own file
    func_list = {}
    starting = False
    curr_search = ""
    curr_index = 0
    for index, x in enumerate(contents.split("\n")):
        if starting:
            # end of function if this line is empty and last line
            if not x.split() and not contents[index + 1][0].isspace():
                func_list[curr_search] = (curr_index, index)
                curr_search = ""
                starting = False
        elif x[0:3] == "def":
            starting = True
            curr_index = index + 1
            curr_search = re.split("\s|\(", x)[1]
    # return dictionary with function name and location in file
    return func_list


class AnalyzeCode:
    '''Runs through contents once - appending, analyzing, and deleting previous code'''
    one_indent = "    "
    updates = []
    add_funcs = []
    special_words = ["def", "if", "elif", "else", "try",
                     "except", "for", "class", "with", "while", "finally"]
    classRun = False
    # classRun checks to make run function only runs once

    def __init__(self, c, f, num):
        self.func_list = f
        self.contents = c
        # if this is the original file, don't remove duplicates (there are none)
        self.remove_dup = (True if (num > 2) else False)

    def is_number(self, n):
        # returns if str value is a number
        try:
            float(n)
            return True
        except ValueError:
            pass
        try:
            import unicodedata
            unicodedata.numeric(n)
            return True
        except (TypeError, ValueError):
            pass
            return False

    def add_info(self, file_spec):
        # add information about previous file - learning about size, location, runtime...
        os_stat_list = ["MODE", "INO", "DEV", "NLINK", "UID", "GID", "SIZE",
                        "ATIME", "MTIME", "CTIME", "FILENUM", "PID", "PREVFILENAME"]
        file_name = file_spec[2]
        file_spec = list(os.stat(file_name)) + file_spec
        new_file_spec = "PREVIOUS_FILE_SPEC = {"
        for i, x in enumerate(file_spec):
            x_key = "\"" + os_stat_list[i] + "\":"
            x_val = str(x)
            if self.is_number(x):
                new_file_spec += x_key + x_val + ","
            else:
                new_file_spec += x_key + "\"" + x_val + "\"}"
        self.contents = self.contents.split("\n")
        if self.contents[0][0] == "p":
            self.contents[0] = new_file_spec
        else:
            self.contents.insert(0, new_file_spec)
        self.contents = "\n".join(self.contents)

    def add_func(self, func_content):
        # adds functions to a list to append while looping file lines
        self.add_funcs.append(func_content)

    def rewrite(self, line, where, what):
        self.updates.append([line, where, what])

    # def resolve_issues(self):
    #     for thing in self.updates:

    def is_between(self, num1, arr):
        return (bool(arr) and num1 >= arr[0] and num1 <= arr[1])

    async def run(self, done):
        # check if we've already called AnalyzeCode().run() before and stop if he have
        if not self.classRun:
            loop_content = self.contents.split("\n")
            placeholder = []
            remove = ()
            remove_line = False
            add_this = ""
            for index, x in enumerate(loop_content):
                await asyncio.sleep(0)
                if self.add_funcs:
                    if "import" in x and not loop_content[index + 1].split():
                        # adds the new functions after all the import statements
                        x += "\n\n" + "\n".join(self.add_funcs)
                        self.add_funcs = []
                    placeholder.append(x)
                elif not self.is_between(index + 1, remove):
                    if add_this:
                        placeholder.append(add_this)
                        add_this = ""
                    remove = ()
                    if self.updates:
                        if x.split():
                            f_word = x.split()[0]
                            # f_word is the first word in a line - example: else, if, for...
                            func_name = re.split("\s|\(", x)[1]
                            # func_name splits a line like "def function_name(things):" into "function_name"
                        else:
                            f_word = ""
                            func_name = ""
                        indents = ""
                        for z, y in enumerate(x):
                            if not y.isspace():
                                break
                            else:
                                indents += y
                        # if this line has the code parameter in it
                        line_appended = False
                        updates_placeholder = self.updates
                        self.updates = []
                        for q, arr in enumerate(updates_placeholder):
                            if arr[0] in x:
                                what = indents + arr[2]
                                if f_word in self.special_words:
                                    what = self.one_indent + what
                                if (not line_appended):
                                    line_appended = True
                                    placeholder.append(x)
                                    if (not arr[1] == "prepend") and func_name in self.func_list:
                                        remove = self.func_list[func_name]
                                    if arr[1] == "prepend":
                                        placeholder.append(what)
                                    elif arr[1] == "append":
                                        remove_line = False
                                        add_this = what
                                    elif arr[1] == "remove":
                                        placeholder.append(what)
                                        remove_line = True
                                else:
                                    if not arr[1] == "prepend":
                                        if not remove and func_name in self.func_list:
                                            remove = self.func_list[func_name]
                                        if arr[1] == "remove":
                                            placeholder.append(what)
                                        elif arr[1] == "append":
                                            add_this += (what if not add_this else "\n" + what)
                                    else:
                                        placeholder.append(what)
                                # self.updates.remove(arr)
                            else:
                                self.updates.append(arr)
                        # end of inside for loop
                        placeholder.append(x) if not line_appended else None
                    else:
                        placeholder.append(x)
                elif not remove_line:
                    placeholder.append(x)
            self.contents = "\n".join(placeholder)
            self.classRun = True
            done()


    def __str__(self):
        # simple return of the file_contents
        return self.contents


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

    def run_once(self):
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
            asyncio.ensure_future(func(arg, self.set_result))
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()


class Crawler:
    '''Crawler searches a websites, finds relative links, and code tags to check if content is valid python'''

    log_file = "./out.log"

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
        links = list(set([self.handle_links(url,link) for link in links if (link and (self.initials[0] in link or not "." in link))]))
        await asyncio.sleep(random.uniform(0.1, 0.9))
        self.log(links)
        done()

    def log(self, info):
        if type(info) == type([]):
            out_file = "./json_dump" + str(self.file_num) + ".json"
            print("Dumping Contents into " + out_file)
            data = {'links': info}
            with open(out_file, 'w') as outfile:
                json.dump(data, outfile)
            print("JSON dumped")
        else:
            info = "\nfile_dump " + str(self.file_num) + "\n\n" + info
            with open(self.log_file, 'a') as outfile:
                outfile.write(info)
            print("Information logged")
        # works as callback, for TaskManager

if __name__ == "__main__":
    file_num = int(re.findall(r'\d+', __file__)[0])
    # next conditional here for a catch, so the files do not stack up in **development**
    if file_num > 3:
        quit()
    file_open = open(__file__, "r")
    file_number = int(file_num) + 1
    file_content = file_open.read()
    func_list = split_by_func(file_content)
    # code for initializing AnalyzeCode class
        # analyze = AnalyzeCode(file_content, func_list, file_number)
        # analyze.add_info([file_number - 1, os.getpid(), __file__])
        # analyze.add_func('''def stop_process(pid):\n    newfile = open(\"newtext.txt\",\"w\");newfile.write(str(pid));newfile.close()''')
        # analyze.rewrite("def run_next_file", "prepend", "print(\"things\")")
        # analyze.rewrite("def run_next_file", "append", '''print("not things")''')
        # analyze.rewrite("def split_by_func", "remove", '''stuff = 5''')
        # analyze.rewrite("if __name__ ==", "prepend", "newfile = open(\"newtext.txt\",\"w\");newfile.write(\"coolbeans\");newfile.close() if __file__ == 'analyze2.py' else quit()")
        # analyze.rewrite("if __name__ ==", "append", "stop_process(os.getpid())")
    # end of that code
    crawl = Crawler(["stackoverflow.com"], file_num)
    manage = TaskManager()
    # run crawler and analyecode main functions asynchronously - they require more processing time
    # manage.add_func(crawl.get_links())
    # manage.add_func(analyze.run())
    manage.run_once()
    # run_next_file(str(analyze), file_number)
