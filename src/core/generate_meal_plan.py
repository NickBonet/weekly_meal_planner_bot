import datetime
import os
from urllib.parse import urlencode, urljoin

import requests
from requests.structures import CaseInsensitiveDict


def get_todays_meal():
    url = os.environ.get("MEALIE_API") + "/api/households/mealplans/today"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer " + os.environ.get("MEALIE_API_TOKEN")
    resp = requests.get(url, headers=headers)
    return resp.json()


def get_tomorrows_meal():
    # get tomorrow's date a YYYY-MM-DD
    tomorrow_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )

    base_url = os.environ.get("MEALIE_API")
    endpoint = "/api/households/mealplans"
    params = {
        "page": 1,
        "perPage": -1,
        "start_date": tomorrow_date,
        "end_date": tomorrow_date,
    }

    url = urljoin(base_url, endpoint) + "?" + urlencode(params)

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer " + os.environ.get("MEALIE_API_TOKEN")
    resp = requests.get(url, headers=headers)
    # if resp contains items, return the items array
    if resp.json() and "items" in resp.json():
        return resp.json()["items"]
    elif resp.json() and "detail" in resp.json() and "Could not validate credentials" in resp.json()["detail"]:
        return resp.json()
    else:
        return None
