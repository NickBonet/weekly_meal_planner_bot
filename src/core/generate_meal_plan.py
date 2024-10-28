import os

import requests
from requests.structures import CaseInsensitiveDict


def get_todays_meal():
    url = os.environ.get("MEALIE_API") + "/api/households/mealplans/today"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer " + os.environ.get("MEALIE_API_TOKEN")
    resp = requests.get(url, headers=headers)
    return resp.json()
