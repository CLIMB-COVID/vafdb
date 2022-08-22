import os
import ast
import json
import argparse
import requests
import basecount
import pandas as pd



class VAFDBClient():
    DEFAULT_HOST = "localhost"
    DEFAULT_PORT = 8000
    MESSAGE_BAR_WIDTH = 0


    def __init__(self, host=None, port=None):
        if host is None:
            host = VAFDBClient.DEFAULT_HOST
            
        if port is None:
            port = VAFDBClient.DEFAULT_PORT
        
        self.url = f"http://{host}:{port}"
        self.endpoints = {
            "create" : os.path.join(self.url, "data/"),
            "get" : os.path.join(self.url, "data/")
        }


    @classmethod
    def _format_response(cls, response, pretty_print=True):
        '''
        Make the response look lovely
        '''
        if pretty_print:
            indent = 4
        else:
            indent = None
        status_code = f"<[{response.status_code}] {response.reason}>".center(VAFDBClient.MESSAGE_BAR_WIDTH, "=")
        return f"{status_code}\n{json.dumps(response.json(), indent=indent)}"


    def create(self, metadata=None, tsv=None, csv=None):
        if not (bool(metadata) ^ bool(tsv) ^ bool(csv)):
            raise Exception("Must provide exactly one of the following: metadata dict, tsv file or csv file")

        if metadata:
            # Run basecount on the BAM
            bc = basecount.BaseCount(
                metadata["bam_path"], 
                min_base_quality=10, 
                min_mapping_quality=10
            )

            # Format metadata that will be emitted as JSON
            metadata = {
                "pathogen" : metadata["pathogen"],
                "central_sample_id" : metadata["central_sample_id"],
                "run_name" : metadata["run_name"],
                "published_name" : metadata["published_name"],
                "collection_date" : metadata["collection_date"],
                "fasta_path" : metadata["fasta_path"],
                "bam_path" : metadata["bam_path"],
                "lineage" : metadata["lineage"],
                "primer_scheme" : metadata["primer_scheme"],
                "vaf" : [],
                "num_vafs" : 0,
            }

            # Format vafs within metadata JSON
            for record in bc.records():
                max_pc = max(record["pc_a"], record["pc_c"], record["pc_g"], record["pc_t"], record["pc_ds"])
                if record["coverage"] >= 20:
                    if max_pc <= 90 or (90 < max_pc <= 95 and record["secondary_entropy"] <= 0.4):
                        metadata["vaf"].append(
                            {
                                "reference" : record["reference"],
                                "position" : record["position"],
                                "coverage" : record["coverage"],
                                "num_a" : record["num_a"],
                                "num_c" : record["num_c"],
                                "num_g" : record["num_g"],
                                "num_t" : record["num_t"],
                                "num_ds" : record["num_ds"],
                                "entropy" : record["entropy"],
                                "secondary_entropy" : record["secondary_entropy"]
                            }
                        )

            # Calculate number of vafs
            metadata["num_vafs"] = len(metadata["vaf"])
            
            # Send data
            response = requests.post(
                self.endpoints["create"], 
                json=metadata
            )
            print(VAFDBClient._format_response(response))
    

    def get(self, fields=None):
        if fields is None:
            fields = {}
        
        response = requests.get(
            self.endpoints["get"],
            params=fields
        )
        if response.ok:
            if response.json():
                meta_fields = list(response.json()[0].keys())
                meta_fields.pop(meta_fields.index("vaf"))
            else:
                meta_fields = None
            table = pd.json_normalize(
                response.json(), 
                record_path=["vaf"], 
                meta=meta_fields
            )
            print(table.to_csv(index=False, sep='\t'), end='')

            # table = pd.json_normalize(response.json()["results"])
            # print(table.to_csv(index=False, sep='\t'), end='')

            # next = response.json()["next"]
            # while next is not None:
            #     response = requests.get(next)
            
            #     if response.ok:
            #         next = response.json()["next"]
            #         table = pd.json_normalize(response.json()["results"])
            #         print(table.to_csv(index=False, sep='\t', header=False), end='')
            #     else:
            #         next = None
            #         print(VAFDBClient._format_response(response))
        else:
            print(VAFDBClient._format_response(response))



def main():
    url_parser = argparse.ArgumentParser(add_help=False)
    url_parser.add_argument("--host", default="localhost")
    url_parser.add_argument("--port", default="8000")

    parser = argparse.ArgumentParser()
    command = parser.add_subparsers(dest="command")
    
    create_parser = command.add_parser("create", parents=[url_parser])
    create_parser.add_argument("--dict")
    create_parser.add_argument("--tsv")
    create_parser.add_argument("--csv")

    get_parser = command.add_parser("get", parents=[url_parser])
    get_parser.add_argument("-f", "--field", nargs=2, action="append", metavar=("FIELD", "VALUE"))
    
    args = parser.parse_args()

    client = VAFDBClient(
        host=args.host,
        port=args.port 
    )

    if args.command == "create":
        if args.dict:
            metadata = ast.literal_eval(args.dict)
        else:
            metadata = None
        
        client.create(
            metadata=metadata,
            tsv=args.tsv,
            csv=args.csv
        )
    
    elif args.command == "get":
        fields = {}
        if args.field is not None:
            for f, v in args.field:
                if fields.get(f) is None:
                    fields[f] = []
                fields[f].append(v)
        client.get(fields)



if __name__ == "__main__":
    main()
