import ast
import argparse
import requests
import basecount


def create(url, args):
    endpoint = f"{url}/api/create/"
    
    # Transform string to dictionary 
    record = ast.literal_eval(args.data)

    # Run basecount on the BAM
    bc = basecount.BaseCount(record["bam_path"], min_base_quality=10, min_mapping_quality=10)

    if bc.mean_entropy(min_coverage=20) <= 0.12:
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
            "vafs" : [],
            "num_vafs" : 0,
        }

        # Format vafs within metadata JSON
        for record in bc.records():
            max_pc = max(record["pc_a"], record["pc_c"], record["pc_g"], record["pc_t"], record["pc_ds"])
            if record["coverage"] >= 20:
                if max_pc <= 90 or (90 < max_pc <= 95 and record["secondary_entropy"] <= 0.4):
                    metadata["vafs"].append(
                        {
                            "reference" : record["reference"],
                            "position" : record["position"],
                            "coverage" : record["coverage"],
                            "num_a" : record["num_a"],
                            "num_c" : record["num_c"],
                            "num_g" : record["num_g"],
                            "num_t" : record["num_t"],
                            "num_ds" : record["num_ds"]
                        }
                    )

        # Calculate number of vafs and upload
        metadata["num_vafs"] = len(metadata["vafs"])
        response = requests.post(endpoint, json=metadata)
        print(response)


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
    # Execute corresponding function for the chosen action subparser
    actions[args.action](url, args)


if __name__ == "__main__":
    main()