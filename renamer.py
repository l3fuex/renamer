#!/usr/bin/python3
"""Renaming of movie and tv-show files"""

try:
    import sys
    import os
    import re
    import configparser
    import parser
    import imdb
except ModuleNotFoundError as error:
    print("[ERROR] {}".format(error))
    raise SystemExit from None


config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.ini"))
KEY = config.get("IMDB", "apikey")
LANG = config.get("IMDB", "language")


def input_validation():
    """Validation of user input.

    sys.argv is being searched for valid options and invalid file arguments.
    If a valid option is found, it gets deleted from sys.argv and
    an according value is asigned to the option variable.
    Also for any invalid file arguments the entry in sys.argv gets deleted
    so that sys.argv only consists of valid file arguments.

    Returns:
        options (dict): options in key value format
    """
    # define default options and valid file extensions
    options = {"debug": False, "simulate": False}
    extensions = [".avi", ".mkv", ".mov", ".mp4", ".wmv"]

    # remove program call from arguments
    sys.argv.remove(sys.argv[0])

    # print help if no arguments are specified
    if not sys.argv:
        print_help()
        raise SystemExit from None

    # validation of options arguments
    index = 0
    while index < len(sys.argv):
        if re.match("^-.*", sys.argv[index]):
            if sys.argv[index] == "-s" or sys.argv[index] == "--simulate":
                options["simulate"] = True
                sys.argv.remove(sys.argv[index])
            elif sys.argv[index] == "-v" or sys.argv[index] == "--verbose":
                options["debug"] = True
                sys.argv.remove(sys.argv[index])
            elif sys.argv[index] == "-h" or sys.argv[index] == "--help":
                print_help()
                raise SystemExit from None
            else:
                print("[ERROR] One or more arguments are not supported")
                raise SystemExit from None
        else:
            index += 1

    # print error if no file is specified
    if not sys.argv:
        print("[ERROR] Please specify at least one file")
        raise SystemExit from None

    # validation of file arguments
    index = 0
    while index < len(sys.argv):
        if not os.path.isfile(sys.argv[index]):
            print(f'[ERROR] File "{sys.argv[index]}" not found')
            sys.argv.remove(sys.argv[index])
        elif not os.path.splitext(sys.argv[index])[1] in extensions:
            print(f'[ERROR] File "{sys.argv[index]}" is not a media file')
            sys.argv.remove(sys.argv[index])
        else:
            index += 1

    # raise SystemExit if there are no valid file arguments
    if not sys.argv:
        raise SystemExit from None

    return options


def print_help():
    """Prints out a general help page about how to use the program."""
    print("Usage:")
    print("    renamer [ -s ] [ -v ] [ -h ] [ file 1 ] [ file 2 ] [ file n ]")
    print("")
    print("Arguments:")
    print("    -s, --simulate")
    print("            no action")
    print("    -v, --verbose")
    print("            verbose output")
    print("    -h, --help ")
    print("            help page")
    print("")
    print("Examples:")
    print("    ./renamer Alien.mkv")
    print("    ./renamer Alien.mkv Predator.mkv")
    print("    ./renamer Futurama*.mkv")
    print("    ./renamer Futurama/Season\\ {01..03}/*.mkv")


def imdb_lookup(metadata, ptitle=None, pseason=None, presponse=None, debug=False):
    """Lookup imdb data for given metadata.

    The lookup logic consists of three modes to minimize API calls to the
    absolute minimun. The three modes are search, title and batch mode.

    The main purpose of the search mode is to get an imdb ID for given
    metadata information. Starting with the most specific search request
    leading to less specific requests the mode can be called up to three
    times. The purpose of this behaviour is to minimize user interactions.
    If there is no search result after the last iteration an error will be
    raised.

    Either if search mode finds a result or if an imdb ID is already present
    in the metadata information, the logic will continue in title mode.
    In this mode the actual needed information will be retrieved over the
    imdb API.

    The batch mode is optional and only needed to minimize API calls.
    It's main purpose is to detect bulk renaming of series and return cached
    information of the previous API call. To do so the arguments 'previous
    title', 'previous season' and 'previous response' are needed.
    Further batch mode works only on sorted data structures.

    metadata data structure:
    {
      "extension": ".mkv",
      "filename": "Alien (1979)",
      "dirname": "/path/to/my/file",
      "runtime": 116,
      "year": "1979",
      "type": "movie",
      "title": "Alien 1979"
      "id": "tt0078748"
    }
    title and type are mandatory, anything else is optional in this context

    Args;
        metadata (dict): dictionary containing metadata information
        ptitle (str): previous title needed for batch mode
        pseason (str): previous season needed for batch mode
        presponse (dict): previous response needed for batch mode
        debug (bool): enable / disable debug output

    Returns:
        response (dict): API response
    """
    asflag = False
    while True:
        # batch mode
        if metadata["title"] == ptitle:
            if debug:
                print("[DEBUG] entering batch mode")
            if metadata["type"] == "series" and metadata["season"] == pseason:
                return presponse
            if metadata["type"] == "series" and metadata["season"] != pseason:
                data = imdb.get_episodes(KEY, LANG, presponse["id"], metadata["season"], debug)
                presponse.update(data)
                return presponse
        # title mode
        elif "id" in metadata:
            if debug:
                print("[DEBUG] entering title mode")
            if metadata["type"] == "movie":
                response = imdb.get_title(KEY, LANG, metadata["id"], debug)
                return response
            if metadata["type"] == "series":
                response = imdb.get_title(KEY, LANG, metadata["id"], debug)
                data = imdb.get_episodes(KEY, LANG, metadata["id"], metadata["season"], debug)
                response.update(data)
                return response
        # advanced search mode
        elif asflag:
            if debug:
                print("[DEBUG] entering advanced search mode")
            if metadata["type"] == "series":
                metadata.pop("runtime", None)
            search = imdb.advanced_search(KEY, metadata["type"], metadata["title"], metadata.get("year"), metadata.get("runtime"), debug)
            index = select_result(search)
            if index is None:
                if "year" in metadata:
                    metadata.pop("year")
                    continue
                if "runtime" in metadata:
                    metadata.pop("runtime")
                    continue
                if "year" and "runtime" not in metadata:
                    asflag = False
                    continue
            metadata["id"] = search["results"][index]["id"]
        # basic search mode
        else:
            if debug:
                print("[DEBUG] entering basic search mode")
            if metadata["type"] == "movie":
                search = imdb.search_movie(KEY, LANG, metadata["title"], debug)
            if metadata["type"] == "series":
                search = imdb.search_series(KEY, LANG, metadata["title"], debug)
            index = select_result(search)
            if index is None:
                raise ValueError("nothing found for title " + "\"" + metadata["title"] + "\"")
            metadata["id"] = search["results"][index]["id"]


def select_result(response):
    """Select the correct result from an imdb search request and get
    the corresponding index value.

    If there is only one entry in the given search response the index value
    will be set to 0 and the processing ends. If there are more than one
    entries in the search response the user is asked to make a choice.
    The corresponding index value will then be returned.
    Any other condition will return 'None' as index value.

    Args:
        response (dict): imdb-api search response

    Returns:
        index (int): corresponding index value
    """
    if len(response["results"]) == 1:
        index = 0

    elif len(response["results"]) > 1:
        for index, result in enumerate(response["results"]):
            print("{}: {}, {}".format(
                index + 1,
                result["title"],
                result["description"]
                )
            )
        while True:
            print("enter your choice:")
            index = input()
            # check if input is a number
            if not index.isdigit():
                print("only numbers are allowed as input")
                continue
            index = int(index)
            # check if number is in correct range
            if index < 1 or index > len(response["results"]):
                print("choose a number between 1 and {}".format(len(response["results"])))
                continue
            index -= 1
            break

    else:
        index = None

    return index


def main():
    """Renaming of movie and tv-show files."""
    # input processing
    options = input_validation()

    print("[INFO] Start processing {} file(s)".format(len(sys.argv)))

    # sort arguments for further processing (important for batch mode)
    sys.argv.sort()

    ptitle, pseason, response = None, None, None
    for i in sys.argv:
        # parse files in sys.argv
        filedata = parser.file_parser(i, options["debug"])
        infodata = parser.info_parser(i, options["debug"])
        metadata = {}
        metadata.update(filedata)
        metadata.update(infodata)

        # collect data from imdb
        try:
            response = imdb_lookup(metadata, ptitle, pseason, response, options["debug"])
            ptitle = metadata["title"]
            pseason = metadata.get("season")
        except ValueError as error:
            print("[ERROR] {}".format(error))
            continue
        else:
            imdb_data = parser.dict_parser(response, ["id", "title", "year", "genres"])
            if metadata["type"] == "series":
                episode = int(metadata["episode"]) - 1
                data = parser.dict_parser(response["episodes"][episode], ["episodeTitle"])
                imdb_data.update(data)
            metadata.update(imdb_data)

        # build new filename
        if metadata["type"] == "movie":
            newname = (
                metadata["title"]
                + " (" + metadata["year"] + ")"
                + metadata["extension"]
            )
        if metadata["type"] == "series":
            newname = (
                metadata["title"]
                + " - S" + str(metadata["season"])
                + "E" + metadata["episode"]
                + " - " + metadata["episodeTitle"]
                + metadata["extension"]
            )

        # sanitize filename
        newname = re.sub(r"[\*\?<>\"|\\/]", "", newname)
        newname = re.sub(":", "\ua789", newname)
        newname = re.sub(" {2,}", " ", newname)

        # build path
        newname = os.path.join(metadata["dirname"], newname)

        # rename file
        try:
            if not options["simulate"]:
                os.rename(i, newname)
            print('[INFO] Renaming "{}" to "{}"'.format(os.path.basename(i), os.path.basename(newname)))
        except OSError as error:
            print("[ERROR] {}".format(error))
            continue

    print("[INFO] Finished!")


if __name__ == "__main__":
    main()
