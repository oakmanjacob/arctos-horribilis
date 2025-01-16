"""Basic Arctos API Python Client

This package is designed to mimic the functionality of the ArctosR package by providing bare bones
access to Arctos Data using the Arctos API. To use this package, you must have already requested an
Arctos API key for your project and added that to your computer's environment variables under
ARCTOS_API_KEY.

I have added basic rate limiting so as to avoid stressing out Arctos and, by extension, Dusty and
Michelle. However, don't take this as a license to go wild. I'm sure there are ways to be a bother
despite the guard rails I've put in place.

We rate limit each type of API call to 1 request every 10 seconds.

Client Functions
    * get_query_parameters() - Returns the columns which can be filtered on in get_records
    * get_result_parameters() - Returns the columns which can be included in a get_records result
    * get_records() - Used to actually pull records from Arctos

The Arctos API works via a series of calls to the server. The first call defines the query and
caches the query results into a temporary table which can be subsequently queried to get the actual
records. Queries to the cached results can only return 100 records at a time and thus we end up
hitting the API many times for even relatviely limited queries.

Why they did this, I can't say. People just liked it better that way.
"""

import os
import operator
import requests
import itertools

from concurrent.futures import ThreadPoolExecutor
from functools import reduce
from ratelimit import limits, sleep_and_retry
from backoff import on_exception, expo

API_URL = "https://arctos.database.museum/component/api/v2/catalog.cfc"
API_KEY = os.environ.get("ARCTOS_API_KEY")
BATCH_SIZE = 100  # This batch size is based on the arctos api
THREAD_COUNT = 4


@on_exception(expo, requests.exceptions.Timeout, max_tries=3)
@sleep_and_retry
@limits(calls=1, period=10)
def get_query_parameters():
    """Calls the Arctos API to get the columns which can be filtered on in get_records."""

    params = {
        "method": "about",
        "queryformat": "struct",
        "api_key": API_KEY,
    }

    response = requests.get(API_URL, params, timeout=200)
    return response.json()["QUERY_PARAMS"]


@on_exception(expo, requests.exceptions.Timeout, max_tries=3)
@sleep_and_retry
@limits(calls=1, period=10)
def get_result_parameters():
    """Calls the Arctos API to get the columns which can be included in a get_records result."""

    params = {
        "method": "about",
        "queryformat": "struct",
        "api_key": API_KEY,
    }

    response = requests.get(API_URL, params, timeout=200)
    return response.json()["RESULTS_PARAMS"]


def get_records(query: dict, columns: list = None, limit: int = None):
    """Gets filtered specimen records from Arctos.
    
    Args:
        query: A dictionary defining a list of columns to filter.
        columns: A list of the columns which should be returned in the final result.
        limit: The maximum number of records to return.
    
    Returns:
        A list of dictionaries which represent each record returned by the query.
    """

    initial_response = call_query_api(query, columns, limit)

    total_records = limit or initial_response["recordsTotal"]
    table = initial_response["tbl"]

    pool = ThreadPoolExecutor(max_workers=THREAD_COUNT)
    responses = pool.map(call_table_api,
                         itertools.repeat(table),
                         range(0, total_records, BATCH_SIZE))
    pool.shutdown()

    return reduce(operator.concat, [response["DATA"] for response in responses])


@on_exception(expo, requests.exceptions.Timeout, max_tries=3)
@sleep_and_retry
@limits(calls=1, period=10)
def call_query_api(query: dict, columns: list = None, limit: int = None):
    """Internal function for making an initial query to Arctos and getting the cached table name."""

    if query is not None:
        params = query

    if columns is not None:
        params["cols"] = ",".join(columns)

    if limit is not None:
        params["length"] = limit

    params["method"] = "getCatalogData"
    params["queryformat"] = "struct"
    params["api_key"] = API_KEY

    return requests.get(API_URL, params).json()


@on_exception(expo, requests.exceptions.Timeout, max_tries=3)
@sleep_and_retry
@limits(calls=1, period=10)
def call_table_api(table: str, start: int = 0):
    """Internal function for pulling records from a cached query result table."""

    params = {
        "method": "getCatalogData",
        "queryformat": "struct",
        "api_key": API_KEY,
        "tbl": table,
        "start": start,
        "length": BATCH_SIZE,
    }

    response = requests.get(API_URL, params, timeout=200)
    return response.json()
