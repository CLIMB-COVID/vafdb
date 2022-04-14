import pysam
import sys
import pathlib

bampath = pathlib.Path(sys.argv[1])
refpath = pathlib.Path(sys.argv[2])

with pysam.AlignmentFile(bampath, "rb", reference_filename=refpath) as bam:
    out_dict = {pos: 0 for pos in range(0, bam.lengths[0] + 1)}
    for read in bam:
        if read.is_supplementary or read.is_unmapped:
            continue
        out_dict[read.reference_start] += 1
        out_dict[read.reference_end] += 1

for pos, count in out_dict.items():
    print(f"{pos + 1}\t{count}", file=sys.stdout)

