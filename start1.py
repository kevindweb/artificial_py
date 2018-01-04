#for system commands
import os
#for function testing
import timeit
#regex split commands
import re

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
                func_list[curr_search] = [curr_index,index]
                curr_search = ""
                starting = False
        elif x[0:3] == "def":
            starting = True
            curr_index = index + 1
            curr_search = re.split("\s|\(",x)[1]
    # return dictionary with function name and location in file
    return func_list

class AnalyzeCode:
    '''Runs through contents once - appending, analyzing, and deleting previous code'''
    self.one_indent = "    "
    self.rewrite = []
    self.add_funcs = []
    self.special_words = ["def","if","elif","else","try","except","for","class","with","while","finally"]
    def __init__(self, c, f, num):
        self.func_list = f
        self.contents = c
        # if this is the original file, don't remove duplicates (there are none)
        self.remove_dup = (True if (num > 2) else False)

    def is_number(n):
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
        classRun = False
        # classRun checks to make sure it only runs once
        for i,x in enumerate(file_spec):
            x_key = "\"" + os_stat_list[i] + "\":"
            x_val = str(x)
            if is_number(x):
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
        self.rewrite.append([line, where, what])

    def run(self):
        if not classRun:
        # check if we've already called AnalyzeCode().run() before and stop if he have
            loop_content = self.contents.split("\n")
            placeholder = []
            for index,x in enumerate(loop_content):
                placeholder.append(x)
                # loop through everyline
            # python keywords that require indenting afterwards
            # where = where to put new code... (prepend = right after line; append = at the end of the conditional or func)
            searching = False
            remove = False
            add_lines = False
            removeUntil = 0
            for index,x in enumerate(contents):
                # if this line has the code parameter in it
                if line in x and not add_lines:
                    indents = ""
                    for z,y in enumerate(x):
                        if not y.isspace():
                            break
                        else:
                            indents += y
                    what = indents + what
                    f_word = x.split()[0]
                    # f_word is the first word in a line - example: else, if, for...
                    func_name = re.split("\s|\(",x)[1]
                    # this splits a line like "def function_name(things):" into "function_name"
                    if functions and func_name in functions:
                        removeUntil = functions[func_name][1]
                        # remove lines until variable == the line number
                    if f_word in special_words:
                        what = one_indent + what
                    if where == "prepend":
                        new_contents.append(x)
                        new_contents.append(what)
                    elif where == "append":
                        searching = True
                        new_contents.append(x)
                        # if after function, append "what" at end
                    elif where == "remove":
                        new_contents.append(x)
                        new_contents.append(what)
                        remove = True
                        searching = True
                        # find function or conditional contents, replace all with "what" parameter
                    add_lines = True
                elif searching:
                    if removeUntil:
                        if index < removeUntil + 1:
                            if not remove:
                                new_contents.append(x)
                    else:
                        if not remove:
                            new_contents.append(what)
                        new_contents.append(x)
                        searching = False
                        remove = False
                    #print("searching for end of function")
                else:
                    #if not searching:
                    new_contents.append(x)
            self.contents = "\n".join(placeholder)
            classRun = True

    __str__(self):
        # simple return of the file_contents
        return self.contents


if __name__ == "__main__":
    file_num = int(re.findall(r'\d+',__file__)[0])
    # here for a catch, so the files do not stack up in development
    if file_num > 3:
        quit()
    file_open = open(__file__,"r")
    file_number = int(file_num) + 1
    file_content = file_open.read()
    func_list = split_by_func(file_content)
    go = AnalyzeCode(file_content, func_list, file_number)
    go.add_func('''def stop_process(pid):\n    newfile = open(\"newtext.txt\",\"w\");newfile.write(str(pid));newfile.close()''')
    go.add_info([file_number - 1, os.getpid(), __file__])
    go.rewrite("def write_next_file", "prepend", "print(\"things\")")
    go.rewrite("if __name__ ==", "prepend", "newfile = open(\"newtext.txt\",\"w\");newfile.write(\"coolbeans\");newfile.close() if __file__ == 'start2.py' else quit()")
    go.rewrite("if __name__ ==", "append", "stop_process(os.getpid())")
    go.run()
    # run_next_file(str(go), file_number)
