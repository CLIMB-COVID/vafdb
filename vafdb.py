import ast
import argparse
import requests
import basecount


def create(url, args):
    endpoint = f"{url}/api/create/"

    row = ast.literal_eval(args.json)
    bc = basecount.BaseCount(row["bam_path"], min_base_quality=30, min_mapping_quality=20)
    mean_entropy = bc.mean_entropy(min_coverage=20)

    if mean_entropy <= 0.15:

        metadata = {
            "pathogen" : row["pathogen"],
            "central_sample_id" : row["central_sample_id"],
            "run_name" : row["run_name"],
            "published_name" : row["published_name"],
            "collection_date" : row["collection_date"],
            "fasta_path" : row["fasta_path"],
            "bam_path" : row["bam_path"],
            "lineage" : row["lineage"],
            "primer_scheme" : row["primer_scheme"],
            "vafs" : [],
            "num_vafs" : 0,
        }

        for record in bc.records():
            max_pc = max(record["pc_a"], record["pc_c"], record["pc_g"], record["pc_t"], record["pc_ds"])
            if record["coverage"] >= 20  and (max_pc <= 90 or (max_pc <= 95 and record["secondary_entropy"] <= 0.4)):
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

        metadata["num_vafs"] = len(metadata["vafs"])
        response = requests.post(endpoint, json=metadata)
        print(f"{response}: {response.reason}")



def main():
    actions = {
        "create" : create
    }

    parser = argparse.ArgumentParser()
    action = parser.add_subparsers(dest="action")
    
    # get_parser = action.add_parser("get")
    # get_action = get_parser.add_subparsers(dest="get_action")
    # get_central_sample_id = get_action.add_parser("central_sample_id")
    # get_central_sample_id_action = get_central_sample_id.add_subparsers(dest="get_central_sample_id_action")
    # get_central_sample_id_action_is = get_central_sample_id_action.add_parser("is")
    # get_central_sample_id_action_is.add_argument("central_sample_id")
    # get_central_sample_id_action_like = get_central_sample_id_action.add_parser("like")
    # get_central_sample_id_action_like.add_argument("central_sample_id")
    
    create_parser = action.add_parser("create")
    create_parser.add_argument("json")
    create_parser.add_argument("--host", default="localhost")
    create_parser.add_argument("--port", default="8000")

    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}"

    # if args.action == "get":
    #     if args.get_action == "central_sample_id":
    #         endpoint = "http://localhost:8000/get/central_sample_id/"
    #         response = requests.get(endpoint, params={"central_sample_id" : args.central_sample_id, "action" : args.get_central_sample_id_action})
    #         print(response.json())

    actions[args.action](url, args)


if __name__ == "__main__":
    main()