#!/usr/bin/python3
"""Renaming of movie and tv-show files"""

import sys
import os
import re
import parser
import imdb


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


def select_result(response):
    """Select the correct result from an imdb search request and get
    the corresponding index value.

    If there is only one entry in the given search response the index value
    will be set to 0 and the processing ends. If there are more than one
    entries in the search response the user is asked to make a choise.
    The corresponding index value will then be returned.
    Any other condition will raise an error.

    Args:
        response (dict): imdb-api search response

    Returns:
        index (int): corresponding index value
    """
    if len(response["results"]) == 1:
        index = 0

    elif len(response["results"]) > 1:
        for index, result in enumerate(response["results"]):
            print("{}: {}, {}, [{}]".format(
                index + 1,
                result["title"],
                result["description"],
                result["resultType"]
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
        raise ValueError("no search results found for \"" + response["expression"] + "\"")

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
        filedata = parser.file_parser(i)
        infodata = parser.info_parser(i)
        metadata[i] = {}
        metadata[i].update(filedata)
        metadata[i].update(infodata)

    # collect data from imdb
    prevtitle, prevseason = None, None
    for i in metadata:
        try:
            # batch mode
            if metadata[i]["title"] == prevtitle:
                if options["debug"]:
                    print("[DEBUG] entering batch mode")
                if metadata[i]["type"] == "series" and metadata[i]["season"] != prevseason:
                    metadata[i]["id"] = search["results"][index]["id"]
                    data = imdb.get_episodes(metadata[i]["id"], metadata[i]["season"], options["debug"])
                    response.update(data)
            # title mode
            elif "id" in metadata[i]:
                if options["debug"]:
                    print("[DEBUG] entering title mode")
                if metadata[i]["type"] == "movie":
                    response = imdb.get_title(metadata[i]["id"], options["debug"])
                if metadata[i]["type"] == "series":
                    response = imdb.get_title(metadata[i]["id"], options["debug"])
                    data = imdb.get_episodes(metadata[i]["id"], metadata[i]["season"], options["debug"])
                    response.update(data)
            # search mode
            else:
                if options["debug"]:
                    print("[DEBUG] entering search mode")
                if metadata[i]["type"] == "movie":
                    search = imdb.search_movie(metadata[i]["title"], options["debug"])
                    index = select_result(search)
                    metadata[i]["id"] = search["results"][index]["id"]
                    response = imdb.get_title(metadata[i]["id"], options["debug"])
                if metadata[i]["type"] == "series":
                    search = imdb.search_series(metadata[i]["title"], options["debug"])
                    index = select_result(search)
                    metadata[i]["id"] = search["results"][index]["id"]
                    response = imdb.get_title(metadata[i]["id"], options["debug"])
                    data = imdb.get_episodes(metadata[i]["id"], metadata[i]["season"], options["debug"])
                    response.update(data)
        except ValueError as error:
            print("[ERROR] {}".format(error))
            continue

        # save title and season for next iteration (needed for batch mode)
        prevtitle = metadata[i]["title"]
        prevseason = metadata[i].get("season")

        # add imdb data to meta data
        imdb_data = parser.dict_parser(response, ["id", "title", "year", "genres"])
        if metadata[i]["type"] == "series":
            episode = int(metadata[i]["episode"]) - 1
            data = parser.dict_parser(response["episodes"][episode], ["episodeTitle"])
            imdb_data.update(data)
        metadata[i].update(imdb_data)

        # build new name
        if metadata[i]["type"] == "movie":
            newname = (
                metadata[i]["title"]
                + " (" + metadata[i]["year"] + ")"
                + metadata[i]["extension"]
            )
            newname = os.path.join(metadata[i]["dirname"], newname)
        if metadata[i]["type"] == "series":
            newname = (
                metadata[i]["title"]
                + " - S" + str(metadata[i]["season"])
                + "E" + metadata[i]["episode"]
                + " - " + metadata[i]["episodeTitle"]
                + metadata[i]["extension"]
            )
            newname = os.path.join(metadata[i]["dirname"], newname)

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
