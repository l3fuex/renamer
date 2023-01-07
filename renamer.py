#!/usr/bin/python3
"""Renaming of movie and tv-show files"""

try:
    import sys
    import os
    import re
    import parser
    import imdb
except ModuleNotFoundError as error:
    print("[ERROR] {}".format(error))
    raise SystemExit from None


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


def imdb_lookup(metadata, ptitle, pseason, debug):
    while True:
        # batch mode
        print(metadata["title"])
        print(ptitle)
        if metadata["title"] == ptitle:
            print(metadata["season"])
            print(pseason)
            if debug:
                print("[DEBUG] entering batch mode")
            if metadata["type"] == "series" and metadata["season"] == pseason:
                break
            if metadata["type"] == "series" and metadata["season"] != pseason:
                metadata["id"] = search["results"][index]["id"]
                data = imdb.get_episodes(metadata["id"], metadata["season"], debug)
                response.update(data)
                break
        # title mode
        elif "id" in metadata:
            if debug:
                print("[DEBUG] entering title mode")
            if metadata["type"] == "movie":
                response = imdb.get_title(metadata["id"], debug)
                break
            if metadata["type"] == "series":
                response = imdb.get_title(metadata["id"], debug)
                data = imdb.get_episodes(metadata["id"], metadata["season"], debug)
                response.update(data)
                break
        # search mode
        else:
            if debug:
                print("[DEBUG] entering search mode")
            if metadata["type"] == "series":
                metadata.pop("runtime", None)
            search = imdb.advanced_search(metadata["type"], metadata["title"], metadata.get("year"), metadata.get("runtime"), debug)
            index = select_result(search)
            if index is None:
                if "year" in metadata and "runtime" in metadata:
                    metadata.pop("year")
                    continue
                if "year" not in metadata and "runtime" in metadata:
                    metadata.pop("runtime")
                    continue
                if "year" in metadata and "runtime" not in metadata:
                    metadata.pop("year")
                    continue
                if "year" not in metadata and "runtime" not in metadata:
                    raise ValueError("nothing found for title " + "\"" + metadata["title"] + "\"")
            metadata["id"] = search["results"][index]["id"]

    return response, metadata["title"], metadata.get("season")


def select_result(response):
    """Select the correct result from an imdb search request and get
    the corresponding index value.

    If there is only one entry in the given search response the index value
    will be set to 0 and the processing ends. If there are more than one
    entries in the search response the user is asked to make a choise.
    The corresponding index value will then be returned.
    Any other condition will return 'None' as index value.

    Args:
        response (dict): imdb-api search response

    Returns:
        index (int, None): corresponding index value
    """
    if len(response["results"]) == 1:
        index = 0

    elif len(response["results"]) > 1:
        for index, result in enumerate(response["results"]):
            print("{}: {}, {}, [{}]".format(
                index + 1,
                result["title"],
                result["description"],
                result["genres"]
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
    """Renaming of movie and tv-show files.

    +++ Input Validation +++
    sys.argv is being searched for valid options and invalid file arguments.
    If a valid option is found, it gets deleted from sys.argv and
    an according value is asigned to the option variable.
    Also for any invalid file arguments the entry in sys.argv gets deleted
    so that sys.argv only consists of valid file arguments.

    +++ Renaming Logic +++
    For all valid file arguments local meta data is collected which is the
    basis for further api calls. To prevent unnecessary api calls from
    happening three modes of operation are implemented which are search mode,
    title mode and batch mode.
    In search mode the logic searches for possible titles based on the parsed
    title name (2-3 API calls).
    In title mode the imdbID is already known (1-2 API calls).
    And in batch mode cached data is being used (0-1 API calls).
    """

    # +++ Input Validation +++ #

    # define default options and valid file extensions
    options = {"debug": False, "simulate": False}
    extensions = [".avi", ".mkv", ".mov", ".mp4", ".wmv"]

    # remove program call from arguments
    sys.argv.remove(sys.argv[0])

    # print help if no arguments are specified
    if not sys.argv:
        print_help()
        raise SystemExit

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
                raise SystemExit
            else:
                print("[ERROR] One or more arguments are not supported")
                raise SystemExit
        else:
            index += 1

    # print error if no file is specified
    if not sys.argv:
        print("[ERROR] Please specify at least one file")
        raise SystemExit

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
        raise SystemExit

    # +++ Renaming Logic +++ #

    print("[INFO] Start processing {} file(s)".format(len(sys.argv)))

    # sort file arguments for further processing
    # FIXME: consider implementing a more sophisicated sort function
    sys.argv.sort()

    # parse files in sys.argv for related metadata
    metadata = {}
    for i in sys.argv:
        filedata = parser.file_parser(i, options["debug"])
        infodata = parser.info_parser(i, options["debug"])
        metadata[i] = {}
        metadata[i].update(filedata)
        metadata[i].update(infodata)

    ptitle, pseason = None, None
    for i in metadata:
        # collect data from imdb
        try:
            response, ptitle, pseason = imdb_lookup(metadata[i], ptitle, pseason, options["debug"])
        except ValueError as error:
            print("[ERROR] {}".format(error))
            continue

        # add imdb data to meta data
        imdb_data = parser.dict_parser(response, ["id", "title", "year", "genres"])
        if metadata[i]["type"] == "series":
            episode = int(metadata[i]["episode"]) - 1
            data = parser.dict_parser(response["episodes"][episode], ["episodeTitle"])
            imdb_data.update(data)
        metadata[i].update(imdb_data)

        # build new filename
        if metadata[i]["type"] == "movie":
            newname = (
                metadata[i]["title"]
                + " (" + metadata[i]["year"] + ")"
                + metadata[i]["extension"]
            )
        if metadata[i]["type"] == "series":
            newname = (
                metadata[i]["title"]
                + " - S" + str(metadata[i]["season"])
                + "E" + metadata[i]["episode"]
                + " - " + metadata[i]["episodeTitle"]
                + metadata[i]["extension"]
            )

        # sanitizing filename
        newname = re.sub(r"[<>\"/\\|\?\*]", "", newname)
        newname = re.sub("[:]", " - ", newname)
        newname = re.sub(" {2,}", " ", newname)

        # build path
        abspath = os.path.join(metadata[i]["dirname"], newname)

        # rename file
        try:
            if not options["simulate"]:
                os.rename(i, abspath)
            print('[INFO] Renaming "{}" to "{}"'.format(os.path.basename(i), os.path.basename(abspath)))
        except OSError as error:
            print("[ERROR] {}".format(error))
            continue

    print("[INFO] Finished!")


if __name__ == "__main__":
    main()
