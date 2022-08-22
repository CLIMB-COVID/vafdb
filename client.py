import os
import ast
import argparse
import requests
import basecount


def create(url, args):
    endpoint = os.path.join(url, "data/")
    
    # Transform string to dictionary 
    record = ast.literal_eval(args.data)

    # Run basecount on the BAM
    bc = basecount.BaseCount(
        record["bam_path"], 
        min_base_quality=10, 
        min_mapping_quality=10
    )

    # Format metadata that will be emitted as JSON
    metadata = {
        "pathogen" : record["pathogen"],
        "central_sample_id" : record["central_sample_id"],
        "run_name" : record["run_name"],
        "published_name" : record["published_name"],
        "collection_date" : record["collection_date"],
        "fasta_path" : record["fasta_path"],
        "bam_path" : record["bam_path"],
        "lineage" : record["lineage"],
        "primer_scheme" : record["primer_scheme"],
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
        endpoint, 
        json=metadata
    )
    print(f"{response}: {response.reason}")
    if not response.ok:
        print(response.text)


def main():
    parser = argparse.ArgumentParser()
    action = parser.add_subparsers(dest="action")
    create_parser = action.add_parser("create")
    create_parser.add_argument("data")
    create_parser.add_argument("--host", default="localhost")
    create_parser.add_argument("--port", default="8000")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}" 
    
    actions = {
        "create" : create
    }

    actions[args.action](url, args)


if __name__ == "__main__":
    main()