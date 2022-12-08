import argparse
import pandas as pd
from vafdbclient import version, utils
from vafdbclient.api import Client


class CLI:
    def __init__(self, host="localhost", port=8000):
        self.client = Client(host=host, port=port)

    def create(self, fields):
        fields = utils.construct_unique_fields_dict(fields)
        creation = self.client.create(fields)
        utils.print_response(creation)

    def csv_create(self, csv_path):
        creations = self.client.csv_create(csv_path)
        utils.execute_uploads(creations)

    def tsv_create(self, tsv_path):
        creations = self.client.csv_create(tsv_path, delimiter="\t")
        utils.execute_uploads(creations)

    def get(self, fields):
        fields = utils.construct_fields_dict(fields)

        results = self.client.get(fields)

        result = next(results)

        meta_fields = None
        columns = None

        if result.ok:
            if result.json()["results"]:
                meta_fields = list(result.json()["results"][0].keys())
                meta_fields.pop(meta_fields.index("vaf"))

            table = pd.json_normalize(
                result.json()["results"], record_path=["vaf"], meta=meta_fields
            )
            if meta_fields is not None:
                columns = (
                    [meta_fields[0]]
                    + table.columns.tolist()[: -len(meta_fields)]
                    + table.columns.tolist()[-len(meta_fields) + 1 :]
                )
                table = table[columns]

            print(table.to_csv(index=False, sep="\t"), end="")
        else:
            utils.print_response(result)

        for result in results:
            if result.ok:
                table = pd.json_normalize(
                    result.json()["results"], record_path=["vaf"], meta=meta_fields
                )
                if (meta_fields is not None) and (columns is not None):
                    table = table[columns]

                print(table.to_csv(index=False, sep="\t", header=False), end="")
            else:
                utils.print_response(result)


def run(args):
    if args.command:
        cli = CLI(args.host, args.port)

        if args.command == "create":
            cli.create(args.field)

        elif args.command == "csv-create":
            cli.csv_create(args.csv)

        elif args.command == "tsv-create":
            cli.tsv_create(args.tsv)

        elif args.command == "get":
            cli.get(args.field)


def get_args():
    url_parser = argparse.ArgumentParser(add_help=False)
    url_parser.add_argument("--host", default="localhost")
    url_parser.add_argument("--port", default="8000")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=version.__version__,
        help="Client version number.",
    )

    command = parser.add_subparsers(dest="command", metavar="{command}")

    create_parser = command.add_parser("create", parents=[url_parser])
    create_parser.add_argument(
        "-f", "--field", nargs=2, action="append", metavar=("FIELD", "VALUE")
    )

    csv_create_parser = command.add_parser("csv-create", parents=[url_parser])
    csv_create_parser.add_argument("csv")

    tsv_create_parser = command.add_parser("tsv-create", parents=[url_parser])
    tsv_create_parser.add_argument("tsv")

    get_parser = command.add_parser("get", parents=[url_parser])
    get_parser.add_argument(
        "-f", "--field", nargs=2, action="append", metavar=("FIELD", "VALUE")
    )

    args = parser.parse_args()

    return args


def main():
    args = get_args()
    run(args)
