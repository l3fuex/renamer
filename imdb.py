#!/usr/bin/python3
"""Implementation of the IMDB API"""

try:
    import json
    import configparser
    import os
    import requests
except ModuleNotFoundError as error:
    print("[ERROR] {}".format(error))
    raise SystemExit from None


config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))

BASE_URL = "https://imdb-api.com"
KEY = config.get("IMDB", "apikey")
LANG = config.get("IMDB", "language")


def check_key():
    """Raises a SystemExit if no API key is present."""
    if not KEY:
        print("[ERROR] No API key!")
        raise SystemExit


def search_movie(movie_title, debug=False):
    """Builds the SearchMovie API call.

    Args:
        movie_title (string): search string
        debug (boolean): enable / disbale debug output

    Returns:
        api_call (dict): API response
    """
    check_key()
    # build api call
    url = (
        BASE_URL + "/" +
        LANG + "/" +
        "API/SearchMovie" + "/" +
        KEY + "/" +
        movie_title
    )
    if debug:
        print("[DEBUG] sending api call {}".format(url))
    return api_call(url)


def search_series(series_title, debug=False):
    """Builds the SearchSeries API call.

    Args:
        series_title (string): search string
        debug (boolean): enable / disbale debug output

    Returns:
        api_call (dict): API response
    """
    check_key()
    # build api call
    url = (
        BASE_URL + "/" +
        LANG + "/" +
        "API/SearchSeries" + "/" +
        KEY + "/" +
        series_title
    )
    if debug:
        print("[DEBUG] sending api call {}".format(url))
    return api_call(url)


def advanced_search(media_type, title, year, runtime, debug=False):
    """Builds the AdvancedSearch API call."""
    check_key()
    # build api call
    if media_type == "movie":
        string = "&title_type=feature,tv_movie,video"
    if media_type == "series":
        string = "&title_type=tv_series,tv_miniseries"
    if year is not None:
        string += "&release_date=" + str(year) + "-01-01," + str(year) + "-12-31"
    if runtime is not None:
        string += "&runtime=" + str(runtime-5) + "," + str(runtime+5)
    url = (
        BASE_URL + "/" +
        "API/AdvancedSearch" + "/" +
        KEY + "?" +
        "title=" + title +
        string
    )
    if debug:
        print("[DEBUG] sending api call {}".format(url))
    return api_call(url)


def get_title(imdb_id, debug=False):
    """Builds the Title API call.

    Args:
        imdb_id (string): imdbID
        debug (boolean): enable / disbale debug output

    Returns:
        api_call (dict): API response
    """
    check_key()
    # build api call
    url = (
        BASE_URL + "/" +
        LANG + "/" +
        "API/Title" + "/" +
        KEY + "/" +
        imdb_id
    )
    if debug:
        print("[DEBUG] sending api call {}".format(url))
    return api_call(url)


def get_episodes(imdb_id, season, debug=False):
    """Builds the SeasonEpisode API call.

    Args:
        imdb_id (string): imdbID
        season (string): season number
        debug (boolean): enable / disbale debug output

    Returns:
        api_call (dict): API response
    """
    check_key()
    # build api call
    url = (
        BASE_URL + "/" +
        LANG + "/" +
        "API/SeasonEpisodes" + "/" +
        KEY + "/" +
        imdb_id + "/" +
        season
    )
    if debug:
        print("[DEBUG] sending api call {}".format(url))
    response = api_call(url)

    # rename key to prevent problems in further processing with duplicate keys
    data = response["episodes"]
    for i in range(len(data)):
        response["episodes"][i]["episodeTitle"] = data[i]["title"]
        response["episodes"][i].pop("title")

    return response


def api_call(url):
    """Sends a request with a given API call.

    Args:
        url (string): API call

    Returns:
        api_call (dict): API response
    """
    try:
        response = json.loads(requests.get(url).text)
        if response["errorMessage"]:
            raise ValueError("unexpected API response: \"" + response["errorMessage"] + "\"")
    except requests.exceptions.ConnectionError as error:
        print("[ERROR] {}".format(error))
        raise SystemExit from None
    else:
        return response
