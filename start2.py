previous_file_spec = {"MODE":33188,"INO":8591611201,"DEV":16777220,"NLINK":1,"UID":501,"GID":20,"SIZE":4741,"ATIME":1514929588,"MTIME":1514929585,"CTIME":1514929585,"FILENUM":2,"PID":49282,"PREVFILENAME":"start1.py"}
import os
import timeit
import re

def stop_process(pid):
    os.system("kill " + str(pid))

def write_next_file(contents, file):
    print("things")
    fh = open(file,"w")
    fh.write(contents)

def run_next_file(contents, num):
    file = "./start" + num + ".py"
    write_next_file(contents, file)
    # os.system("python " + file)
    # quit()

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
        return False

def split_by_func(contents):
    func_list = {}
    starting = False
    curr_search = ""
    curr_index = 0
    contents = contents.split("\n")
    for index,x in enumerate(contents):
        if starting:
            if not x.split() and not contents[index + 1][0].isspace():
                func_list[curr_search] = [curr_index,index]
                curr_search = ""
                starting = False
        elif x[0:3] == "def":
            starting = True
            curr_index = index + 1
            curr_search = re.split("\s|\(",x)[1]
    return func_list

def add_func(content, func_content):
    content = content.split("\n")
    for index,x in enumerate(content):
        if "import" in x and not content[index + 1].split():
            x += "\n\n" + func_content
            content[index] = x
            break
    return "\n".join(content)

def rewrite(contents, line, where, what, one_indent, functions=None):
    special_words = ["def","if","elif","else","try","except","for","class","with","while","finally"]
    contents = contents.split("\n")
    new_contents = []
    searching = False
    removeUntil = 0
    remove = False
    add_lines = False
    for index,x in enumerate(contents):
        if add_lines:
            new_contents.append(x)
        elif line in x:
            indents = ""
            for z,y in enumerate(x):
                if not y.isspace():
                    break
                else:
                    indents += y
            what = indents + what
            f_word = x.split()[0]
            func_name = re.split("\s|\(",x)[1]
            if functions and func_name in functions:
                removeUntil = functions[func_name][1]
            if f_word in special_words:
                what = one_indent + what
            if where == "prepend":
                new_contents.append(x)
                new_contents.append(what)
                add_lines = True
            elif where == "append":
                searching = True
                new_contents.append(x)
                # if after function, append "what" at end
            elif where == "remove":
                new_contents.append(x)
                new_contents.append(what)
                remove = True
                searching = True
                # find function or conditional contents, replace all with "what"
        elif searching:
            if removalUntil:
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
    return "\n".join(new_contents)

def add_info(content, file_spec):
    os_stat_list = ["MODE", "INO", "DEV", "NLINK", "UID", "GID", "SIZE", "ATIME", "MTIME", "CTIME", "FILENUM", "PID", "PREVFILENAME"]
    file_name = file_spec[2]
    file_spec = list(os.stat(file_name)) + file_spec
    new_file_spec = "previous_file_spec = {"
    for i,x in enumerate(file_spec):
        x_key = "\"" + os_stat_list[i] + "\":"
        x_val = str(x)
        if is_number(x):
            new_file_spec += x_key + x_val + ","
        else:
            new_file_spec += x_key + "\"" + x_val + "\"}"
    content = content.split("\n")
    if content[0][0] == "p":
        content[0] = new_file_spec
    else:
        content.insert(0, new_file_spec)
    return "\n".join(content)

if __name__ == "__main__":
    this_file = __file__.split(".")[0]
    file_open = open(__file__,"r")
    file_number = str(int(this_file[5:len(this_file)]) + 1)
    file_content = file_open.read()
    func_list = split_by_func(file_content)
    file_content = rewrite(file_content, "def write_next_file", "prepend", "print(\"things\")", "    ", func_list)
    file_content = add_func(file_content, '''def stop_process(pid):\n    os.system("kill " + str(pid))''')
    file_content = add_info(file_content, [file_number, os.getpid(), __file__])
    run_next_file(file_content, file_number)
