import csv
import sys
import requests
import concurrent.futures
from django_query_tools.client import F


class Client:
    def __init__(self, host="localhost", port=8000):
        self.url = f"http://{host}:{port}"
        self.endpoints = {
            "generate": lambda project: f"{self.url}/data/generate/{project}/",
            "filter": lambda project: f"{self.url}/data/filter/{project}/",
            "query": lambda project: f"{self.url}/data/query/{project}/",
            "delete": lambda project, sample_id: f"{self.url}/data/delete/{project}/{sample_id}/",
        }

    def generate(self, project, fields):
        """
        Generate VAFs from metadata.
        """
        response = requests.post(
            url=self.endpoints["generate"](project),
            json=fields,
        )
        return response

    def csv_generate(self, project, csv_path, delimiter=None, multithreaded=True):
        """
        "Generate VAFs from metadata provided via CSV/TSV."
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

            record = next(reader, None)

            if record:
                response = requests.post(
                    url=self.endpoints["generate"](project),
                    json=record,
                )
                yield response

                if multithreaded:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        futures = [
                            executor.submit(
                                requests.post,
                                url=self.endpoints["generate"](project),
                                json=record,
                            )
                            for record in reader
                        ]
                        for future in concurrent.futures.as_completed(futures):
                            yield future.result()
                else:
                    for record in reader:
                        response = requests.post(
                            url=self.endpoints["generate"](project),
                            json=record,
                        )
                        yield response
        finally:
            if csv_file is not sys.stdin:
                csv_file.close()

    def filter(self, project, fields=None):
        """
        Filter VAFs and their metadata.
        """
        if fields is None:
            fields = {}

        response = requests.get(
            url=self.endpoints["filter"](project),
            params=fields,
        )
        yield response

        if response.ok:
            _next = response.json()["next"]
        else:
            _next = None

        while _next is not None:
            response = requests.get(
                url=_next,
            )
            yield response

            if response.ok:
                _next = response.json()["next"]
            else:
                _next = None

    def query(self, project, query=None):
        """
        Query VAFs and their metadata.
        """
        if query:
            if not isinstance(query, F):
                raise Exception("Query must be an F object")
            else:
                query = query.query

        response = requests.post(
            url=self.endpoints["query"](project),
            json=query,
        )
        yield response

        if response.ok:
            _next = response.json()["next"]
        else:
            _next = None

        while _next is not None:
            response = requests.post(
                url=_next,
                json=query,
            )
            yield response

            if response.ok:
                _next = response.json()["next"]
            else:
                _next = None

    def delete(self, project, sample_id):
        """
        "Delete VAFs and their metadata."
        """
        response = requests.delete(
            url=self.endpoints["delete"](project, sample_id),
        )
        return response

    def csv_delete(self, project, csv_path, delimiter=None):
        """
        Delete VAFS from metadata provided via CSV/TSV."
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
                sample_id = record.get("sample_id")
                if sample_id is None:
                    raise KeyError("sample_id column must be provided")

                response = requests.delete(
                    url=self.endpoints["delete"](project, sample_id),
                )
                yield response
        finally:
            if csv_file is not sys.stdin:
                csv_file.close()
