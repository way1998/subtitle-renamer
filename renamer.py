import sys, getopt, os


# print usage of this program
def help():
    msg = '''usage: renamer.py
             -d --directory: path to the directory
             -m --match: match string in format '<parent>=<child>' directly preceding the index, e.g. 'S02E=Season 2 EP'
             -n --number: number of digits of the index
             -p --parent: parent (video file) extension
             -c --child: child (subtitle file) extension
             -h: print usage
          '''
    print(msg)


# parse command line arguments
def parse(argv):
    # print help if no arguments are provided
    if len(argv) == 0:
        help()
        sys.exit()

    # get arguments
    directory = ''
    match = []
    number = 0
    parent = ''
    child = ''

    try:
        opts, args = getopt.getopt(argv, "hd:m:n:p:c:", ["directory=", "match=", "number=", "parent=", "child="])
    except getopt.GetoptError:
        help()
        sys.exit("invalid arguments")
    
    for opt, arg in opts:
        if opt == "-h":
            help()
            sys.exit()
        elif opt in ("-d", "--directory"):
            directory = arg
        elif opt in ("-m", "--match"):
            match = arg.split("=")
        elif opt in ("-n", "--number"):
            number = arg
        elif opt in ("-p", "--parent"):
            parent = arg
        elif opt in ("-c", "--child"):
            child = arg

    # validate arguments
    if len(directory) == 0:
        sys.exit("no directory")
    elif len(match) != 2:
        sys.exit("invalid match string format")
    elif len(number) == 0:
        sys.exit("invalid number of digits of the index")
    elif len(parent) == 0:
        sys.exit("no parent extension")
    elif len(child) == 0:
        sys.exit("no child extension")

    # return arguments
    return directory, match, number, parent, child


# get lists of parent and child files with corresponding extensions
def get_files(directory, parent, child):
    parents = []
    children = []

    for file in os.listdir(directory):
        if file.endswith("." + parent):
            parents.append(os.path.join(directory, file))
        elif file.endswith("." + child):
            children.append(os.path.join(directory, file))

    return parents, children


# match parent with child files and rename child files
def match_and_rename(parents, children, match, number):
    for child in children:
        # get index
        i = child.find(match[1]) + len(match[1])
        index = child[i:i+int(number)]
        parent_substr = match[0] + index

        # find corresponding parent
        for parent in parents:
            if parent_substr in parent:
                i_ep = parent.rfind(".")
                i_ec = child.rfind(".")
                new_child_path = parent[:i_ep] + child[i_ec:]

                # rename child file
                os.rename(child, new_child_path)


def main(argv):
    # parse arguments
    directory, match, number, parent, child = parse(argv)

    # get parent and child files
    parents, children = get_files(directory, parent, child)

    # match and rename child files
    match_and_rename(parents, children, match, number)
      

if __name__ == "__main__":
    main(sys.argv[1:])