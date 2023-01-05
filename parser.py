#!/usr/bin/python3
"""Various parser implementations."""

try:
    import os
    import re
    import cv2
except ModuleNotFoundError as error:
    print("[ERROR] {}".format(error))
    raise SystemExit from None


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

    # extract filesystem information
    data["extension"] = os.path.splitext(file)[1]
    data["filename"] = os.path.basename(fullname)
    data["dirname"] = os.path.dirname(fullname)

    """
    # extract duration
    video_data = cv2.VideoCapture(file)
    frames = video_data.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = video_data.get(cv2.CAP_PROP_FPS)
    if frames and fps:
        seconds = round(frames / fps)
        data["runtime"] = round(seconds / 60)
    """

    # extract year
    pattern = ".*(19\d\d|20\d\d).*"
    result = re.match(pattern, abspath)
    if result:
        data["year"] = result.group(1)

    # extract media type
    pattern = r"(^.*)(?:[sS])(\d{1,2})(?:[eE])(\d{1,2})(?:.*)"
    result = re.match(pattern, abspath)
    if result:
        data["type"] = "series"
    else:
        data["type"] = "movie"

    # extract season and episode number
    if data["type"] == "series":
        pattern = r"(^.*)(?:[sS])(\d{1,2})(?:[eE])(\d{1,2})(?:.*)"
        result = re.match(pattern, abspath)
        data["season"] = result.group(2)
        data["episode"] = result.group(3)

    # extract title
    pattern = "(?:.*/)(.*)(19|20)(\\d\\d)(.*)(720|1080|2160)(.*)"
    result = re.match(pattern, abspath)
    if result:
        title = result.group(1)
    else:
        title = os.path.basename(fullname)

    title = re.sub(r"(720|1080|2160)[pP]?", "", title)
    title = re.sub(r"[xX]26[4,5]", "", title)
    title = re.sub(r"(blueray|dubbed|repack)", "", title, flags=re.IGNORECASE)
    title = re.sub(r"[sS]\d{1,2}[eE]\d{1,2}.*", "", title)
    title = re.sub(r"[._\-\(\)\[\]]", " ", title)
    title = re.sub(" {2,}", " ", title)

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
    directory = os.path.dirname(os.path.abspath(file))
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
