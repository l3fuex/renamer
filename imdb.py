#!/usr/bin/python3
"""Implementation of the IMDB API"""

try:
    import json
    import requests
except ModuleNotFoundError as error:
    print("[ERROR] {}".format(error))
    raise SystemExit from None


BASE_URL = "https://imdb-api.com"


def check_key(key):
    """Raises a SystemExit if no API key is present.

    Args:
        key (str): API key
    """
    if not key:
        print("[ERROR] No API key!")
        raise SystemExit


def search_movie(key, lang, movie_title, debug=False):
    """Builds the SearchMovie API call.

    Args:
        key (str): API key
        lang (str): language
        movie_title (str): search string
        debug (bool): enable / disbale debug output

    Returns:
        api_call (dict): API response
    """
    check_key(key)
    # build api call
    url = (
        BASE_URL + "/" +
        lang + "/" +
        "API/SearchMovie" + "/" +
        key + "/" +
        movie_title
    )
    if debug:
        print("[DEBUG] sending api call {}".format(url))
    return api_call(url)


def search_series(key, lang, series_title, debug=False):
    """Builds the SearchSeries API call.

    Args:
        key (str): API key
        lang (str): language
        series_title (str): search string
        debug (bool): enable / disbale debug output

    Returns:
        api_call (dict): API response
    """
    check_key(key)
    # build api call
    url = (
        BASE_URL + "/" +
        lang + "/" +
        "API/SearchSeries" + "/" +
        key + "/" +
        series_title
    )
    if debug:
        print("[DEBUG] sending api call {}".format(url))
    return api_call(url)


def advanced_search(key, media_type, title, year, runtime, debug=False):
    """Builds the AdvancedSearch API call.
    Args:
        key (str): API key
        media_type (str): movie or series
        title (str): media title
        year (str): release date
        runtime (int): runtime in minutes
        debug (bool): enable / disbale debug output

    Returns:
        api_call (dict): API response
    """
    check_key(key)
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
        key + "?" +
        "title=" + title +
        string
    )
    if debug:
        print("[DEBUG] sending api call {}".format(url))
    return api_call(url)


def get_title(key, lang, imdb_id, debug=False):
    """Builds the Title API call.

    Args:
        key (str): API key
        lang (str): language
        imdb_id (str): imdbID
        debug (bool): enable / disbale debug output

    Returns:
        api_call (dict): API response
    """
    check_key(key)
    # build api call
    url = (
        BASE_URL + "/" +
        lang + "/" +
        "API/Title" + "/" +
        key + "/" +
        imdb_id
    )
    if debug:
        print("[DEBUG] sending api call {}".format(url))
    return api_call(url)


def get_episodes(key, lang, imdb_id, season, debug=False):
    """Builds the SeasonEpisode API call.

    Args:
        key (str): API key
        lang (str): language
        imdb_id (str): imdbID
        season (str): season number
        debug (bool): enable / disbale debug output

    Returns:
        api_call (dict): API response
    """
    check_key(key)
    # build api call
    url = (
        BASE_URL + "/" +
        lang + "/" +
        "API/SeasonEpisodes" + "/" +
        key + "/" +
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
        url (str): API call

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
