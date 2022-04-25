import pandas as pd
import sys
import argparse
import statistics
import os
import itertools
import scipy.signal as sig


def getPrimerDirection(Primer_ID):
    """Infer the primer direction based on it's ID containing LEFT/RIGHT
    Parameters
    ----------
    Primer_ID : string
        The primer ID from the 4th field of the primer scheme
    """
    if "LEFT" in Primer_ID:
        return "+"
    elif "RIGHT":
        return "-"
    else:
        print("LEFT/RIGHT must be specified in Primer ID", file=sys.stderr)
        raise SystemExit(1)


def bed_to_edge(fn):
    """Parses a bed file and collapses alts into canonical primer sites
    Parameters
    ----------
    fn : str
        The bedfile to parse
    Returns
    -------
    list
        A list of dictionaries, where each dictionary contains a row of the parsed bedfile.
        The available dictionary keys are - Primer_ID, direction, start, end
    """

    # read the primer scheme into a pandas dataframe and run type, length and null checks
    primers = pd.read_csv(
        fn,
        sep="\t",
        header=None,
        names=["chrom", "start", "end", "Primer_ID", "PoolName"],
        dtype={
            "chrom": str,
            "start": int,
            "end": int,
            "Primer_ID": str,
            "PoolName": str,
        },
        usecols=(0, 1, 2, 3, 4),
        skiprows=0,
    )
    if len(primers.index) < 1:
        print("primer scheme file is empty", file=sys.stderr)
        raise SystemExit(1)
    if primers.isnull().sum().sum():
        print("malformed primer scheme file", file=sys.stderr)
        raise SystemExit(1)

    # compute the direction
    primers["direction"] = primers.apply(
        lambda row: getPrimerDirection(row.Primer_ID), axis=1
    )

    # Generate a dict to hold amplicon start / end points

    amplicons = [row["Primer_ID"].split("_")[1] for _, row in primers.iterrows()]
    amplicon_edges = {amplicon: {"s": [], "e": []} for amplicon in amplicons}

    for _, row in primers.iterrows():
        amplicon = row["Primer_ID"].split("_")[1]
        if amplicon_edges.get(amplicon):
            if row["direction"] == "+":
                amplicon_edges[amplicon]["s"].append(row.start)
            else:
                amplicon_edges[amplicon]["e"].append(row.end)

    return amplicon_edges


def pos_check(args, edge_counts, position):

    bg_start = 0 if position - args.bg_range < 0 else position - args.bg_range
    bg_end = position + args.bg_range
    bg_counts = list(edge_counts["count"])[bg_start:bg_end]
    # print(bg_counts)
    # print(list(edge_counts["count"])[position - 1])
    stdev = statistics.stdev(bg_counts)
    mean = statistics.mean(bg_counts)
    threshold = mean + (stdev * args.deviations)
    if list(edge_counts["count"])[position] >= threshold:
        return True
    else:
        return False


def bedcheck(args, bed_edges, edge_counts):
    hits = 0
    positions = [
        edge_dict["s"] + edge_dict["e"] for amplicon, edge_dict in bed_edges.items()
    ]
    positions = list(itertools.chain.from_iterable(positions))
    for position in positions:
        if pos_check(args, edge_counts, position):
            hits += 1

    return hits


def peak_bedcheck(args, bed_edges, edge_peaks):
    positions = [
        edge_dict["s"] + edge_dict["e"] for amplicon, edge_dict in bed_edges.items()
    ]
    positions = set(itertools.chain.from_iterable(positions))

    return len(positions.intersection(edge_peaks))


def find_peaks(edge_counts):
    peaks, _ = sig.find_peaks(edge_counts["count"])
    return set(peaks)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bedfiles", nargs="+", type=os.path.abspath, action="append")
    parser.add_argument("--edge-counts", type=argparse.FileType("r"), default=sys.stdin)
    parser.add_argument("--bg-range", type=int, default=50)
    parser.add_argument("--deviations", type=int, default=3)
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()

    args.bedfiles = [file for file in args.bedfiles[0] if str(file).endswith("bed")]

    if len(args.bedfiles) <= 1:
        print("Supply at least two bed files for comparison with --bedfiles")
        sys.exit(2)

    bed_edges = {str(bedfile): bed_to_edge(bedfile) for bedfile in args.bedfiles}

    edge_counts = pd.read_csv(
        args.edge_counts, sep="\t", names=["pos", "count"], index_col="pos"
    )

    peaks = find_peaks(edge_counts)

    # bed_scores = {
    #     key: bedcheck(args, value, edge_counts) for key, value in bed_edges.items()
    # }

    bed_scores = {
        key: peak_bedcheck(args, value, peaks) for key, value in bed_edges.items()
    }

    winner = max(bed_scores, key=bed_scores.get)

    if not args.report:
        print(winner, file=sys.stdout)
    else:
        for scheme, score in bed_scores.items():
            print(f"{scheme} - {score}", file=sys.stdout)


main()
