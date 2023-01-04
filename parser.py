#!/usr/bin/python3
"""Various parser implementations."""

import os
import re


def file_parser(file):
    """Extracts basic file information like extension, dirname, title.

    Depending, if a special pattern matches the path, the title gets extracted
    either from the dirname or from the filename. The pattern searches for a
    year and the keywords 1080 respectively 720. If the pattern matches, the
    text before the pattern until the next slash is considered to be the title.
    If there is no match the title gets extracted from the filename by cutting
    different keywords from the string.

    Args:
        file (string): file to be parsed

    Returns:
        data (dict): key value pairs of parsed data
    """
    fullname = os.path.splitext(file)[0]
    abspath = os.path.abspath(file)
    data = {}

    # extract title either from dirname or from filename
    pattern = "(?:.*/)(.*)(19|20)(\\d\\d)(.*)(720|1080|2160)(.*)"
    result = re.match(pattern, abspath)
    if result:
        title = result.group(1)
    else:
        title = os.path.basename(fullname)

    # cut keywords from title
    try:
        file_object = open("keywords.txt", "r")
    except Exception as error:
        print("[ERROR] {}".format(error))
        return None
    else:
        content = file_object.readlines()
    finally:
        file_object.close()

    for line in content:
        pattern = line.strip()
        title = re.sub(pattern, "", title, flags=re.IGNORECASE)

    # replace special chars
    title = re.sub("[._\\-\\(\\)\\[\\]]", " ", title)
    title = re.sub(" {2,}", " ", title)

    # match for series pattern
    #pattern = "(^.*)(?:[sS])([1-9]|[0-9][1-9])(?:[eE])(\\d{1,2})"
    pattern = "(^.*)(?:[sS])(\\d{1,2})(?:[eE])(\\d{1,2})"
    result = re.match(pattern, os.path.basename(fullname))
    if result:
        data["type"] = "series"
        data["extension"] = os.path.splitext(file)[1]
        data["filename"] = os.path.basename(fullname)
        data["dirname"] = os.path.dirname(fullname)
        data["title"] = result.group(1).strip()
        data["season"] = result.group(2)
        data["episode"] = result.group(3)
    else:
        data["type"] = "movie"
        data["extension"] = os.path.splitext(file)[1]
        data["filename"] = os.path.basename(fullname)
        data["dirname"] = os.path.dirname(fullname)
        data["title"] = title.strip()

    return data


def info_parser(file):
    """Parses .nfo file related information.

    Searches for related .nfo files, parses them and returns the parsed
    information.

    Args:
        file (string): file to be parsed

    Returns:
        data (dict): key value pairs of parsed data
    """
    fullname = os.path.splitext(file)[0]
    directory = os.path.dirname(file)
    data = {}

    # search for related .nfo file
    for i in os.listdir(directory):
        pattern = ".*" + os.path.basename(fullname) + ".*\\.nfo$"
        result = re.match(pattern, i, re.I)
        if result:
            info_file = os.path.join(directory, i)
            break

    # open file for parsing
    if result and os.path.isfile(info_file):
        try:
            file_object = open(info_file, "rb")
        except Exception as error:
            print("[ERROR] {}".format(error))
            return None
        else:
            content = file_object.read()
            content = str(content)
        finally:
            file_object.close()

        pattern = "https?://(?:www.)?imdb.com/title/(tt\\d*)"
        result = re.findall(pattern, content, re.IGNORECASE)
        if result:
            data["id"] = result[0]

    return data


def dict_parser(dictionary, keys):
    """Parses python dictionaries for specified keys.

    Takes a given dictionary and extracts the specified key value pairs.

    Args:
        dictionary (dict): python dictionary to be parsed
        keys (list): keys which should be extracted

    Returns:
        data (dict): key value pairs of parsed data
    """
    data = {}

    for k, v in dictionary.items():
        if isinstance(v, dict):
            data.update(dict_parser(v, keys))
        if k in keys:
            data[k] = v

    return data
