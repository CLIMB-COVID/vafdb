import argparse
import pandas as pd
from vafdb import version, utils
from vafdb.api import Client


class CLI:
    def __init__(self, host="localhost", port=8000):
        self.client = Client(host=host, port=port)

    def generate(self, project, fields):
        fields = utils.construct_unique_fields_dict(fields)
        result = self.client.generate(project, fields)
        utils.print_response(result)

    def csv_generate(self, project, csv_path, delimiter=None):
        results = self.client.csv_generate(project, csv_path, delimiter=delimiter)
        utils.execute_uploads(results)

    def filter(self, project, fields):
        fields = utils.construct_fields_dict(fields)

        results = self.client.filter(project, fields)

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

    def delete(self, project, sample_id):
        result = self.client.delete(project, sample_id)
        utils.print_response(result)

    def csv_delete(self, project, csv_path, delimiter=None):
        results = self.client.csv_delete(project, csv_path, delimiter=delimiter)
        utils.execute_uploads(results)


def run(args):
    cli = CLI(args.host, args.port)

    if args.command == "generate":
        if args.field:
            cli.generate(args.project, args.field)
        elif args.csv:
            cli.csv_generate(args.project, args.csv)
        elif args.tsv:
            cli.csv_generate(args.project, args.tsv, delimiter="\t")

    elif args.command == "filter":
        cli.filter(args.project, args.field)

    elif args.command == "delete":
        if args.sample_id:
            cli.delete(args.project, args.sample_id)
        elif args.csv:
            cli.csv_delete(args.project, args.csv)
        elif args.tsv:
            cli.csv_delete(args.project, args.tsv, delimiter="\t")


def get_args():
    url_parser = argparse.ArgumentParser(add_help=False)
    url_parser.add_argument(
        "--host", default="localhost", help="Host of VAFDB instance. Default: localhost"
    )
    url_parser.add_argument(
        "--port", default="8000", help="Port number of VAFDB instance. Default: 8000"
    )
    parser = argparse.ArgumentParser(parents=[url_parser])
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=version.__version__,
        help="Client version number.",
    )
    command = parser.add_subparsers(dest="command", metavar="{command}", required=True)
    generate_parser = command.add_parser(
        "generate", help="Generate VAFs from metadata."
    )
    generate_parser.add_argument("project")
    generate_exclusive_parser = generate_parser.add_mutually_exclusive_group(
        required=True
    )
    generate_exclusive_parser.add_argument(
        "-f", "--field", nargs=2, action="append", metavar=("FIELD", "VALUE")
    )
    generate_exclusive_parser.add_argument(
        "--csv", help="Generate VAFs from metadata provided via CSV."
    )
    generate_exclusive_parser.add_argument(
        "--tsv", help="Generate VAFs from metadata provided via TSV."
    )
    filter_parser = command.add_parser("filter", help="Filter VAFs and their metadata.")
    filter_parser.add_argument("project")
    filter_parser.add_argument(
        "-f", "--field", nargs=2, action="append", metavar=("FIELD", "VALUE")
    )
    delete_parser = command.add_parser("delete", help="Delete VAFs and their metadata.")
    delete_parser.add_argument("project")
    delete_exclusive_parser = delete_parser.add_mutually_exclusive_group(required=True)
    delete_exclusive_parser.add_argument(
        "sample_id",
        nargs="?",
        help="[optional] Delete all VAFs for the provided sample_id.",
    )
    delete_exclusive_parser.add_argument(
        "--csv", help="Delete VAFS from metadata provided via CSV."
    )
    delete_exclusive_parser.add_argument(
        "--tsv", help="Delete VAFS from metadata provided via TSV."
    )
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    run(args)
