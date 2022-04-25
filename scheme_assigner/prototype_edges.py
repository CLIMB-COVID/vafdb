import pysam
import sys
import pathlib
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--bamfile", type=pathlib.Path, required=True)
parser.add_argument("--reference", type=pathlib.Path, required=True)
parser.add_argument("--paired", action="store_true")
args = parser.parse_args()


with pysam.AlignmentFile(args.bamfile, "rb", reference_filename=args.reference) as bam:
    out_dict = {pos: 0 for pos in range(0, bam.lengths[0] + 1)}
    for read in bam:
        if read.is_supplementary or read.is_unmapped:
            continue
        if args.paired:
            if read.is_reverse:
                out_dict[read.reference_end] += 1
            else:
                out_dict[read.reference_start] += 1
        else:
            out_dict[read.reference_start] += 1
            out_dict[read.reference_end] += 1

for pos, count in out_dict.items():
    print(f"{pos + 1}\t{count}", file=sys.stdout)

