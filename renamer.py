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
    options = {"asflag": True, "bsflag": True, "simulate": False, "debug": False, "offset": 0}
    extensions = [".avi", ".mkv", ".mov", ".mp4", ".wmv"]

    # remove program call from arguments
    sys.argv.remove(sys.argv[0])

    # print help if no arguments are specified
    if not sys.argv:
        print_help()
        raise SystemExit from None

    # validation of option arguments
    i = 0
    while i < len(sys.argv):
        if re.match("^-.*", sys.argv[i]):
            if sys.argv[i] == "-a" or sys.argv[i] == "--advanced-search":
                options["asflag"] = True
                options["bsflag"] = False
                sys.argv.remove(sys.argv[i])
            elif sys.argv[i] == "-b" or sys.argv[i] == "--basic-search":
                options["asflag"] = False
                options["bsfalg"] = True
                sys.argv.remove(sys.argv[i])
            elif sys.argv[i] == "-s" or sys.argv[i] == "--simulate":
                options["simulate"] = True
                sys.argv.remove(sys.argv[i])
            elif sys.argv[i] == "-v" or sys.argv[i] == "--verbose":
                options["debug"] = True
                sys.argv.remove(sys.argv[i])
            elif sys.argv[i] == "-o" or sys.argv[i] == "--offset":
                try:
                    options["offset"] = int(sys.argv[i+1])
                except ValueError:
                    print("[ERROR] Please specify a valid offset value")
                    raise SystemExit from None
                sys.argv.remove(sys.argv[i+1])
                sys.argv.remove(sys.argv[i])
            elif sys.argv[i] == "-h" or sys.argv[i] == "--help":
                print_help()
                raise SystemExit from None
            else:
                print("[ERROR] One or more arguments are not supported")
                raise SystemExit from None
        else:
            i += 1

    # print error if no file is specified
    if not sys.argv:
        print("[ERROR] Please specify at least one file")
        raise SystemExit from None

    # validation of file arguments
    i = 0
    while i < len(sys.argv):
        if not os.path.isfile(sys.argv[i]):
            print(f'[ERROR] File "{sys.argv[i]}" not found')
            sys.argv.remove(sys.argv[i])
        elif not os.path.splitext(sys.argv[i])[1] in extensions:
            print(f'[ERROR] File "{sys.argv[i]}" is not a media file')
            sys.argv.remove(sys.argv[i])
        else:
            i += 1

    # raise SystemExit if there are no valid file arguments
    if not sys.argv:
        raise SystemExit from None

    return options


def print_help():
    """Prints out a general help page."""
    print("Usage:")
    print("    renamer [options] [file]")
    print("")
    print("Options:")
    print("    -a, --advanced-search  enable only advanced search mode")
    print("    -b, --basic-search     enable only basic search mode")
    print("    -h, --help             show this message")
    print("    -o, --offset           define offset for episode renaming")
    print("    -s, --simulate         no renaming")
    print("    -v, --verbose          verbose output")
    print("")
    print("Examples:")
    print("    renamer Alien.mkv")
    print("    renamer -s Futurama/Season\\ {01..03}/*.mkv")
    print("    renamer -o -1 futurama_S01E03_somename.mkv")


def imdb_lookup(metadata, ptitle=None, pseason=None, presponse=None, asflag=True, bsflag=True, debug=False):
    """Lookup imdb data for given metadata.

    The lookup logic consists of four modes (advanced search mode,
    basic search mode, title mode and batch mode).

    The main purpose of the advanced search mode is to get an imdb ID for
    given metadata information. If no result was found in advanced search
    mode the logic falls back to basic search mode.

    Either if one of the two search modes finds a result or if an imdb ID is
    already present in the metadata information, the logic will continue in
    title mode. In this mode the actual needed information will be retrieved
    over the imdb API.

    The batch mode is optional and only needed to minimize API calls.
    It's main purpose is to detect bulk renaming of series and return cached
    information of the previous API call. To do so the arguments 'previous
    title', 'previous season' and 'previous response' are needed.
    Further, batch mode works only on sorted data structures.

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
    "title" and "type" are mandatory, anything else is optional in this
    context.

    Args:
        metadata (dict): dictionary containing metadata information
        ptitle (str): previous title needed for batch mode
        pseason (str): previous season needed for batch mode
        presponse (dict): previous response needed for batch mode
        asflag (bool): enable / disable advanced search
        bsflag (bool): enable / disable basic search
        debug (bool): enable / disable debug output

    Returns:
        response (dict): API response
    """
    data = metadata.copy()
    while True:
        # batch mode
        if data["title"] == ptitle:
            if debug:
                print("[DEBUG] entering batch mode")
            if data["type"] == "series" and data["season"] == pseason:
                return presponse
            if data["type"] == "series" and data["season"] != pseason:
                tmp = imdb.get_episodes(KEY, LANG, presponse["id"], data["season"], debug)
                presponse.update(tmp)
                return presponse
        # title mode
        elif "id" in data:
            if debug:
                print("[DEBUG] entering title mode")
            if data["type"] == "movie":
                response = imdb.get_title(KEY, LANG, data["id"], debug)
                return response
            if data["type"] == "series":
                response = imdb.get_title(KEY, LANG, data["id"], debug)
                tmp = imdb.get_episodes(KEY, LANG, data["id"], data["season"], debug)
                response.update(tmp)
                return response
        # advanced search mode
        elif asflag:
            if debug:
                print("[DEBUG] entering advanced search mode")
            if data["type"] == "series":
                data.pop("runtime", None)
            search = imdb.advanced_search(KEY, data["type"], data["title"], data.get("year"), data.get("runtime"), debug)
            index = select_result(search)
            if index is not None:
                data["id"] = search["results"][index]["id"]
            elif bsflag:
                asflag = False
            else:
                raise ValueError("nothing found for title " + "\"" + data["title"] + "\"")
        # basic search mode
        elif bsflag:
            if debug:
                print("[DEBUG] entering basic search mode")
            if data["type"] == "movie":
                search = imdb.search_movie(KEY, LANG, data["title"], debug)
            if data["type"] == "series":
                search = imdb.search_series(KEY, LANG, data["title"], debug)
            index = select_result(search, metadata.get("year"))
            if index is not None:
                data["id"] = search["results"][index]["id"]
            else:
                raise ValueError("nothing found for title " + "\"" + data["title"] + "\"")


def select_result(response, year=None):
    """Select the correct result from an imdb search request.

    If there is only one entry in the given search response the index value
    will be set to 0 and the processing ends. If there are more than one
    entries in the search response the logic tries to automatically choose
    the correct result based on the "year". If this is not possible the user
    is asked to make a choice. The corresponding index value will be returned.
    Any other condition will return 'None'.

    Args:
        response (dict): search response
        year (str): year of release

    Returns:
        index (int): corresponding index value
    """
    # exact match
    if len(response["results"]) == 1:
        return 0

    # multiple matches
    if len(response["results"]) > 1:
        # try to automatically select result based on year
        if year is not None:
            count = 0
            for i, v in enumerate(response["results"]):
                if re.match(year, v["description"]):
                    index = i
                    count += 1
            if count == 1:
                return index
        # if no automatic selection is possible ask user to make a choice
        for i, v in enumerate(response["results"]):
            print("{}: {}, {}".format(
                i + 1,
                v["title"],
                v["description"]
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
            return index-1

    # no match
    return None


def main():
    """Renaming of movie and tv-show files."""
    # input validation
    options = input_validation()

    # sort arguments for further processing (important for batch mode)
    sys.argv.sort()

    # process files
    print("[INFO] Start processing {} file(s)".format(len(sys.argv)))
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
            response = imdb_lookup(metadata, ptitle, pseason, response, options["asflag"], options["bsflag"], options["debug"])
            ptitle = metadata["title"]
            pseason = metadata.get("season")
        except ValueError as error:
            print("[ERROR] {}".format(error))
            continue
        else:
            imdb_data = parser.dict_parser(response, ["id", "title", "year", "genres"])
            if metadata["type"] == "series":
                # apply and check offset
                metadata["episode"] = str(int(metadata["episode"]) + options["offset"]).zfill(2)
                episode = int(metadata["episode"])
                if episode < 1 or episode > len(response["episodes"]):
                    print("[ERROR] offset out of range")
                    continue
                data = parser.dict_parser(response["episodes"][episode-1], ["episodeTitle"])
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
                + " - S" + metadata["season"]
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
