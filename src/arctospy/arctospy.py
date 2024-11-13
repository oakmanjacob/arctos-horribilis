import os
from concurrent.futures import ThreadPoolExecutor
import requests
import itertools
import operator
from functools import reduce

API_URL = "https://arctos.database.museum/component/api/v2/catalog.cfc"
API_KEY = os.environ.get("ARCTOS_API_KEY")
BATCH_SIZE = 100 # This batch size is based on the arctos api
THREAD_COUNT = 64

def get_query_parameters():
    params = {
        "method": "about",
        "queryformat": "struct",
        "api_key": API_KEY,
    }

    response = requests.get(API_URL, params, timeout=200)
    return response.json()["QUERY_PARAMS"]

def get_result_parameters():
    params = {
        "method": "about",
        "queryformat": "struct",
        "api_key": API_KEY,
    }

    response = requests.get(API_URL, params, timeout=200)
    return response.json()["RESULTS_PARAMS"]

def call_table_api(table: str, start: int = 0):
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

def call_query_api(query: dict, columns: list = None, limit: int = None):
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

def get_records(query: dict, columns: list = None, limit: int = None):
    initial_response = call_query_api(query, columns, limit)

    total_records = limit or initial_response["recordsTotal"]
    table = initial_response["tbl"]
 
    pool = ThreadPoolExecutor(max_workers=THREAD_COUNT)
    responses = pool.map(call_table_api, itertools.repeat(table), range(0, total_records, BATCH_SIZE))
    pool.shutdown()

    return reduce(operator.concat, [response["DATA"] for response in responses])