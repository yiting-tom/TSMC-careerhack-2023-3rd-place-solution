import dataclasses
import requests
from typing import Any

from utils.logger import L


FIELD_MAPPING = {
    "user": {"user_id", "email", "groups.*"},
    "group": {"group_id"},
    "share": {"share_id", "user.*", "title", "description", "url", "tags.*"},
    "tag": {"tag_id"},
    "dayoff": {"dayoff_id", "time", "user.*"},
}

class Request:
    def __init__(self, resource):
        self._resource = resource
        self._url = f"http://140.116.245.105:33332/items/{resource}"
        self._params = {"fields[]": ""}
        self._fields = FIELD_MAPPING[resource].copy()


class Querier(Request):
    def __init__(self, resource):
        super().__init__(resource)

    def query(self):
        self._params["fields[]"] += ",".join(map(lambda f: f"{f}", self._fields))

        L.info(f"GET {self._resource} from API: url={self._url} params={self._params}")

        response = requests.get(self._url, params=self._params).json()
        if "data" in response:
            return response['data']

    def drop_field(self, field: str):
        if field in self._fields:
            self._fields.remove(field)
        return self
    
    def filter_by(self, field: str, operator: str, values: str):
        key = f"filter{field}[_{operator}]"
        self._params[key] = values if not isinstance(values, list) else ",".join(values)
        return self

class Creator(Request):
    def __init__(self, resource):
        super().__init__(resource)
    
    def __call__(self, obj: Any):
        jsonfied = dataclasses.asdict(obj)
        L.info(f"POST {self._resource} from API: json={jsonfied}")
        response = requests.post(self._url, json=jsonfied)
        return response

class Deleter(Request):
    def __init__(self, resource):
        super().__init__(resource)
    
    def __call__(self, item_id: Any):
        self._url += f"/{item_id}"
        L.info(f"DELETE {self._resource} from API: url={self._url}")
        response = requests.delete(self._url)
        return response

class Updater(Request):
    def __init__(self, resource):
        super().__init__(resource)
    
    def __call__(self, item_id: Any, obj: Any):
        self._url += f"/{item_id}"
        jsonfied = dataclasses.asdict(obj)
        cleaned = {k: v for k, v in jsonfied.items() if v is not None}
        L.info(f"PATCH {self._resource} from API: url={self._url} json={cleaned}")
        response = requests.patch(self._url, json=cleaned)
        return response