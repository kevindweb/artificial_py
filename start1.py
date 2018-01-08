#for system commands
import os
#for function testing
import timeit
#regex split commands
import re
# next two are for website crawling and processing
import bs4 as bs
import requests as req

def run_next_file(contents, num):
    file = "./start" + str(num) + ".py"
    # process replicates, increasing the file number
    fh = open(file,"w")
    fh.write(contents)
    # call the next process to run and quit after process done
    os.system("python " + file)
    quit()

def split_by_func(contents):
    # gets all the names and locations of functions in its own file
    func_list = {}
    starting = False
    curr_search = ""
    curr_index = 0
    for index,x in enumerate(contents.split("\n")):
        if starting:
            # end of function if this line is empty and last line
            if not x.split() and not contents[index + 1][0].isspace():
                func_list[curr_search] = (curr_index,index)
                curr_search = ""
                starting = False
        elif x[0:3] == "def":
            starting = True
            curr_index = index + 1
            curr_search = re.split("\s|\(",x)[1]
    # return dictionary with function name and location in file
    return func_list

class Crawler:
    '''Crawler searches a few websites and relative links for code tags and checks if content is valid python'''
    def __init__(self, websites):
        self.urls = ['http://' + i for i in websites]

    def handle_links(self, url, link):
        return ''.join([url,link]) if link.startswith('/') else link

    def remove_tags(self, content):
        cleanr = re.compile('<.*?>')
        # watch out for escaped characters ie &lt;
        cleantext = re.sub(cleanr, '', content)
        return cleantext

    def get_links(self, url):
        soup = bs.BeautifulSoup(req.get(url).text, 'html.parser')
        body = soup.body
        links = [remove_tags(code) for code in body.find_all('code')]
        #links = [handle_links(url,link) for link in links if "google" in link]
        #links = [str(link.encode("ascii")) for link in links]
        return links

class AnalyzeCode:
    '''Runs through contents once - appending, analyzing, and deleting previous code'''
    def __init__(self, c, f, num):
        self.func_list = f
        self.contents = c
        # if this is the original file, don't remove duplicates (there are none)
        self.remove_dup = (True if (num > 2) else False)
        self.one_indent = "    "
        self.updates = []
        self.add_funcs = []
        self.special_words = ["def","if","elif","else","try","except","for","class","with","while","finally"]
        self.classRun = False
        # classRun checks to make run function only runs once

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
        os_stat_list = ["MODE", "INO", "DEV", "NLINK", "UID", "GID", "SIZE", "ATIME", "MTIME", "CTIME", "FILENUM", "PID", "PREVFILENAME"]
        file_name = file_spec[2]
        file_spec = list(os.stat(file_name)) + file_spec
        new_file_spec = "previous_file_spec = {"
        for i,x in enumerate(file_spec):
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

    def run(self):
        # check if we've already called AnalyzeCode().run() before and stop if he have
        if not self.classRun:
            loop_content = self.contents.split("\n")
            placeholder = []
            remove = ()
            remove_line = False
            add_this = ""
            for index,x in enumerate(loop_content):
                if self.add_funcs:
                    if "import" in x and not loop_content[index + 1].split():
                          # adds the new functions after all the import statements
                          x += "\n\n" + "\n".join(self.add_funcs)
                          print(x)
                          self.add_funcs = []
                    placeholder.append(x)
                elif not self.is_between(index,remove):
                    if self.updates:
                        if x.split():
                            f_word = x.split()[0]
                            # f_word is the first word in a line - example: else, if, for...
                            func_name = re.split("\s|\(",x)[1]
                            # func_name splits a line like "def function_name(things):" into "function_name"
                        else:
                            f_word = ""
                            func_name = ""
                        indents = ""
                        for z,y in enumerate(x):
                            if not y.isspace():
                                break
                            else:
                                indents += y
                        # if this line has the code parameter in it
                        line_appended = False
                        updates_placeholder = self.updates
                        self.updates = []
                        for q,arr in enumerate(updates_placeholder):
                            # print("arr:",arr[0],"line:",x)
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
                                        if arr[1] == "remove":
                                            placeholder.append(what)
                                        elif arr[1] == "append":
                                            add_this += "\n" + what
                                    else:
                                        placeholder.append(what)
                                #self.updates.remove(arr)
                            else:
                                self.updates.append(arr)
                        #end of inside for loop
                        placeholder.append(x) if not line_appended else None
                    else:
                        placeholder.append(x)
                elif not remove_line:
                    placeholder.append(x)
                    if add_this:
                        placeholder.append(add_this)
                        add_this = ""
            self.contents = "\n".join(placeholder)
            self.classRun = True
    def __str__(self):
        # simple return of the file_contents
        return self.contents

# code for initializing AnalyzeCode class

# end of that code

if __name__ == "__main__":
    file_num = int(re.findall(r'\d+',__file__)[0])
    # next conditional here for a catch, so the files do not stack up in **development**
    if file_num > 3:
        quit()
    file_open = open(__file__,"r")
    file_number = int(file_num) + 1
    file_content = file_open.read()
    func_list = split_by_func(file_content)
    start = AnalyzeCode(file_content, func_list, file_number)
    start.add_info([file_number - 1, os.getpid(), __file__])
    #start.add_func('''def stop_process(pid):\n    newfile = open(\"newtext.txt\",\"w\");newfile.write(str(pid));newfile.close()''')
    start.rewrite("def run_next_file", "prepend", "print(\"things\")")
    start.rewrite("def run_next_file", "prepend", '''if "things" == "start":    print("not things")''')
    #start.rewrite("if __name__ ==", "prepend", "newfile = open(\"newtext.txt\",\"w\");newfile.write(\"coolbeans\");newfile.close() if __file__ == 'start2.py' else quit()")
    #start.rewrite("if __name__ ==", "append", "stop_process(os.getpid())")
    start.run()
    run_next_file(str(start), file_number)
