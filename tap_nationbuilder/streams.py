"""Stream type classes for tap-nationbuilder."""

from __future__ import annotations

from pathlib import Path
import requests

from singer_sdk import typing as th  # JSON Schema typing helpers
from cached_property import cached_property

from tap_nationbuilder.client import NationBuilderStream

class ContactsStream(NationBuilderStream):
    """Define custom stream."""

    name = "Contacts"
    path = "/people"
    primary_keys = ["id"]
    replication_key = None
    
    def request_schema(self, url, headers):
        response = requests.get(url, headers=headers)
        self.validate_response(response)
        return response

    def extract_type(self, field):
        if isinstance(field, str):
            return th.StringType
        if isinstance(field, float):
            return th.NumberType
        if isinstance(field, bool):
            return th.BooleanType
        if isinstance(field, int):
            return th.IntegerType
        else:
            return th.StringType

    @cached_property
    def schema(self):
        properties = []
        headers = self.http_headers
        headers.update(self.authenticator.auth_headers or {})
        url = self.url_base + self.path + "/1"
        response = self.request_decorator(self.request_schema)(url, headers=headers)

        fields = response.json().get("person") or dict()
        for field in fields:
            property = th.Property(field, self.extract_type(field))
            properties.append(property)
        return th.PropertiesList(*properties).to_dict()
