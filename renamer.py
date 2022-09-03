import sys, getopt, os


# print usage of this program
def help():
    msg = '''usage: renamer.py
             -d --directory: path to the directory
             -v --video: filename pattern of video files, replace index with "{}", e.g. "S02E{}"
             -s --subtitle: filename pattern of subtitle files, replace index with "#", e.g. "Season 2 EP{}"
             -n --number: number of digits in an index
             -h --help: print usage
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
    patternv = ''
    patterns = ''
    digits = 0

    try:
        opts, args = getopt.getopt(argv, "hd:v:s:n:", ["directory=", "video=", "subtitle=", "number="])
    except getopt.GetoptError:
        help()
        sys.exit("invalid arguments")
    
    for opt, arg in opts:
        if opt == "-h":
            help()
            sys.exit()
        elif opt in ("-d", "--directory"):
            directory = arg
        elif opt in ("-v", "--video"):
            patternv = arg
        elif opt in ("-s", "--subtitle"):
            patterns = arg
            exts = patterns[patterns.rfind('.')+1:]
        elif opt in ("-n", "--number"):
            digits = arg

    # validate arguments
    if len(directory) == 0:
        sys.exit("no directory provided")
    elif len(patternv) == 0:
        sys.exit("no filename pattern of video files provided")
    elif len(patterns) == 0:
        sys.exit("no filename pattern of subtitle files provided")
    elif digits == 0:
        sys.exit("invalid number of index digits")
    elif len(exts) == 0:
        sys.exit("no subtitle file extension specified")

    # return arguments
    return directory, patternv, patterns, digits, exts


# get a list of subtitle files to rename
def get_subtitle_files(directory, exts):
    subtitles = []

    for file in os.listdir(directory):
        if file.endswith("." + exts):
            subtitles.append(os.path.join(directory, file))

    return subtitles


# rename subtitle files based on filename pattern of video files
def match_and_rename(directory, subtitles, patterns, patternv, digits):
    for s in subtitles:
        # get index
        patterns_prefix = patterns[:patterns.find('{}')]
        i = s.find(patterns_prefix) + len(patterns_prefix)
        index = s[i:i+int(digits)]

        # rename subtitle file
        filled = patternv.format(index)
        exts = patterns[patterns.rfind('.')+1:]
        new_name = filled[:filled.rfind('.')+1] + exts
        new_path = os.path.join(directory, new_name)
        os.rename(s, new_path)


def main(argv):
    # parse arguments
    directory, patternv, patterns, digits, exts = parse(argv)

    # get subtitle files
    subtitles = get_subtitle_files(directory, exts)

    # rename subtitle files
    match_and_rename(directory, subtitles, patterns, patternv, digits)
      

if __name__ == "__main__":
    main(sys.argv[1:])