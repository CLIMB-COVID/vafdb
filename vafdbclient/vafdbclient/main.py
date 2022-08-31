import os
import csv
import sys
import json
import argparse
import requests
import pandas as pd
from vafdbclient.version import __version__


def format_response(response, pretty_print=True):
    '''
    Make the response look lovely.
    '''
    if pretty_print:
        indent = 4
    else:
        indent = None
    status_code = f"<[{response.status_code}] {response.reason}>"
    try:
        return f"{status_code}\n{json.dumps(response.json(), indent=indent)}"
    except json.decoder.JSONDecodeError:
        return f"{status_code}\n{response.text}"


class VAFDBClient():
    def __init__(self, host : str = "localhost", port : int = 8000, stdout_responses : bool = False):
        self.url = f"http://{host}:{port}"
        self.endpoints = {
            "create" : os.path.join(self.url, "data/"),
            "get" : os.path.join(self.url, "data/")
        }
        self.stdout_responses = stdout_responses


    def create(self, csv_path : str, delimiter : str | None = None):
        '''
        Insert data into `vafdb`.
        '''
        if csv_path == "-":
            csv_file = sys.stdin
        else:
            csv_file = open(csv_path)

        failures = []
        try:
            if delimiter is not None:
                reader = csv.DictReader(csv_file, delimiter=delimiter)
            else:
                reader = csv.DictReader(csv_file)

            for data in reader:
                response = requests.post(
                    self.endpoints["create"], 
                    json=data
                )
                if self.stdout_responses:
                    print(format_response(response))
                else:
                    try:
                        failures.append(response.json())
                    except json.decoder.JSONDecodeError:
                        failures.append(response.text)
        finally:
            if csv_file is not sys.stdin:
                csv_file.close()
        
        if not self.stdout_responses:
            return failures

    
    def get(self, **fields):
        '''
        Retrieve data from `vafdb`.
        '''
        if fields is None:
            fields = {}
        
        data = []

        response = requests.get(
            self.endpoints["get"],
            params=fields
        )
        if response.ok:
            results = response.json()["results"]

            if results:
                meta_fields = list(results[0].keys())
                meta_fields.pop(meta_fields.index("vaf"))
            else:
                meta_fields = None

            table = pd.json_normalize(
                results, 
                record_path=["vaf"], 
                meta=meta_fields
            )

            if self.stdout_responses:
                print(table.to_csv(index=False, sep='\t'), end='')
            else:
                data.extend(table.to_dict("records"))

            next = response.json()["next"]
            while next is not None:
                response = requests.get(next)
            
                if response.ok:
                    next = response.json()["next"]
                    results = response.json()["results"]
                    
                    table = pd.json_normalize(
                        results, 
                        record_path=["vaf"], 
                        meta=meta_fields
                    )

                    if self.stdout_responses:
                        print(table.to_csv(index=False, sep='\t', header=False), end='')
                    else:
                        data.extend(table.to_dict("records"))
                else:
                    next = None

                    if self.stdout_responses:
                        print(format_response(response))
                    else:
                        try:
                            data = response.json()
                        except json.decoder.JSONDecodeError:
                            data = response.text
                        break
        else:
            if self.stdout_responses:
                print(format_response(response))
            else:
                try:
                    data = response.json()
                except json.decoder.JSONDecodeError:
                    data = response.text
        
        if not self.stdout_responses:
            return data


def run():
    url_parser = argparse.ArgumentParser(add_help=False)
    url_parser.add_argument("--host", default="localhost")
    url_parser.add_argument("--port", default="8000")

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=__version__)
    command = parser.add_subparsers(dest="command")
    
    create_parser = command.add_parser("create", parents=[url_parser])
    file_parser = create_parser.add_mutually_exclusive_group(required=True)
    file_parser.add_argument("--tsv")
    file_parser.add_argument("--csv")

    get_parser = command.add_parser("get", parents=[url_parser])
    get_parser.add_argument("-f", "--field", nargs=2, action="append", metavar=("FIELD", "VALUE"))
    
    args = parser.parse_args()

    if args.command:
        client = VAFDBClient(
            host=args.host,
            port=args.port,
            stdout_responses=True
        )

        if args.command == "create":
            if args.tsv:
                client.create(
                    args.tsv,
                    delimiter="\t"
                )
            else:
                client.create(
                    args.csv,
                )

        elif args.command == "get":
            fields = {}
            if args.field is not None:
                for f, v in args.field:
                    if fields.get(f) is None:
                        fields[f] = []
                    fields[f].append(v)
                    
            client.get(**fields)
