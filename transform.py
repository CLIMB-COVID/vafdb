import sys
import csv
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tsv")
    args = parser.parse_args()

    if args.tsv == '-':
        tsv = sys.stdin
    else:
        tsv = open(args.tsv)

    try:
        reader = csv.DictReader(tsv, delimiter="\t")
        columns = reader.fieldnames
        if columns:
            for row in reader:
                print(row)

    finally:
        if tsv is not sys.stdin:
            tsv.close()


if __name__ == "__main__":
    main()
