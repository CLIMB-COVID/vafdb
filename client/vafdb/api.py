import csv
import sys
import requests
from vafdb.field import Field


class Client:
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.url = f"http://{host}:{port}"
        self.endpoints = {
            "create": f"{self.url}/data/",
            "get": f"{self.url}/data/",
            "query": f"{self.url}/data/query/",
        }

    def create(self, fields):
        """
        Post a metadata record to `VAFDb`.
        """
        response = requests.post(
            self.endpoints["create"],
            json=fields,
        )
        return response

    def csv_create(self, csv_path: str, delimiter: str | None = None):
        """
        Post a .csv or .tsv containing multiple metadata records to `VAFDb`.
        """
        if csv_path == "-":
            csv_file = sys.stdin
        else:
            csv_file = open(csv_path)
        try:
            if delimiter is None:
                reader = csv.DictReader(csv_file)
            else:
                reader = csv.DictReader(csv_file, delimiter=delimiter)

            for record in reader:
                response = requests.post(
                    self.endpoints["create"],
                    json=record,
                )
                yield response
        finally:
            if csv_file is not sys.stdin:
                csv_file.close()

    def get(self, fields=None):
        """
        Retrieve data from `VAFDb`.
        """
        if fields is None:
            fields = {}

        response = requests.get(self.endpoints["get"], params=fields)
        yield response

        if response.ok:
            _next = response.json()["next"]
        else:
            _next = None

        while _next is not None:
            response = requests.get(_next)
            yield response

            if response.ok:
                _next = response.json()["next"]
            else:
                _next = None

    def query(self, query):
        """
        Retrieve data from `VAFDb`.
        """
        if not isinstance(query, Field):
            raise Exception("Query must be of type Field")

        response = requests.post(self.endpoints["query"], json=query.query)
        yield response

        if response.ok:
            _next = response.json()["next"]
        else:
            _next = None

        while _next is not None:
            response = requests.post(_next, json=query.query)
            yield response

            if response.ok:
                _next = response.json()["next"]
            else:
                _next = None
