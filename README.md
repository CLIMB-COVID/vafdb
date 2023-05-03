# `vafdb`

## Setup
Clone the repository:
```
$ git clone https://github.com/CLIMB-COVID/vafdb.git
$ cd vafdb/
```
Create and activate the `vafdb` conda environment:
```
$ conda env create -f environment.yml
$ conda activate vafdb
```
Run the `setup.sh` script to build the client and initialise the database:
```
$ ./setup.sh
```
Then, to start the `vafdb` server, run the `start.sh` script:
```
$ ./start.sh
Starting PIDs: 15292 15293 15294
VAFDB started.
```
To stop the `vafdb` server, run the `stop.sh` script:
```
$ ./stop.sh
Stopping PIDs: 15292 15293 15294
VAFDB stopped.
```

## Create a project
```
$ python manage.py newproject example_project --references /path/to/references.fasta
```
#### Project creation options
```
positional arguments:
  code

options:
  --references REFERENCES
                        Path of FASTA file containing reference sequence(s).
  --description DESCRIPTION
                        [optional] Project description.
  --region REGION       [optional] Specific region to store. Enter in 'CHROM:START-END' format. Default:
                        All regions
  --base-quality BASE_QUALITY
                        [optional] Minimum base quality for storing a VAF. Default: 0
  --mapping-quality MAPPING_QUALITY
                        [optional] Minimum mapping quality for storing a VAF. Default: 0
  --min-coverage MIN_COVERAGE
                        [optional] Minimum coverage for storing a VAF. Default: 0
  --min-entropy MIN_ENTROPY
                        [optional] Minimum entropy for storing a VAF. Default: 0
  --min-secondary-entropy MIN_SECONDARY_ENTROPY
                        [optional] Minimum secondary entropy for storing a VAF. Default: 0
  --insertions          [optional] Store insertion VAFs. Default: False
  --diff-confidence DIFF_CONFIDENCE
                        [optional] Only store VAFs with a different base from the reference, above a
                        certain confidence. Default: None
```
## Delete a project
```
$ python manage.py deleteproject example_project
```

## Generate data for a project
```
$ cat metadata.tsv
sample_id   site   bam_path           collection_date
E21294149D  site1  /path/to/file.bam  2022-10-2
5523DEB355  site6  /path/to/file.bam  2022-9-3
FE3B496871  site2  /path/to/file.bam  2022-5-8
E2A89A963D  site0  /path/to/file.bam  2022-6-5
99508919E2  site1  /path/to/file.bam  2022-10-1
...
```
```
$ vafdb generate example_project --tsv metadata.tsv
<[200] OK>
{
    "project" : "example_project",
    "sample_id": "E21294149D",
    "task_id": "f13e7d1b-b4f6-40fd-890f-b100ca5b27ee"
}
<[200] OK>
{
    "project" : "example_project",
    "sample_id": "5523DEB355",
    "task_id": "ed9ba54b-e1a6-4613-b8f9-12a295544943"
}
<[200] OK>
{
    "project" : "example_project",
    "sample_id": "FE3B496871",
    "task_id": "a77bbf24-f243-498f-938b-d8c8db7ba3ab"
}
<[200] OK>
{
    "project" : "example_project",
    "sample_id": "E2A89A963D",
    "task_id": "851bf18c-53e6-4f47-90be-191f0d8aa976"
}
<[200] OK>
{
    "project" : "example_project",
    "sample_id": "99508919E2",
    "task_id": "88aa7765-847d-437c-abe1-744114577ebb"
}
...
```

## Retrieve data from a project
#### Filtering from the CLI
```
$ vafdb filter example_project --field reference chrom1 --field position__range 250,300
$ vafdb filter example_project --field sample_id E2A89A963D
$ vafdb filter example_project --field position 500 --field collection_date__gt 2023-01-01
```
#### Querying from a python script
```python
# script.py

from vafdb import Client, utils, F

# Initialise the client
client = Client()

# Send a query to the database
# 
# This query asks for all VAFs on chrom1 across all samples
# where there was a C->T or T->C mutation above a confidence
# of 70% and with coverage greater than 50 reads
results = client.query(
    "example_project",
    query=(
        F(reference="chrom1")
        & ((F(ref_base="C") & F(base="T")) | (F(ref_base="T") & F(base="C")))
        & F(confidence__gt=70)
        & F(coverage__gt=50)
    ),
)

# Convert VAFs into a Pandas DataFrame
df = utils.pandafy(results)

# Print the result in tsv format
print(df.to_csv(index=False, sep="\t"), end="")
```
```
$ python script.py
sample_id   ref_base  base  reference   position  coverage  confidence  diff  num_a  num_c  num_g  num_t  num_ds  pc_a   pc_c    pc_g   pc_t    pc_ds  entropy  secondary_entropy  site   bam_path                   
E21294149D  C         T     chrom1  10029     361       91.69       True  1      14     1      331    14      0.277  3.878   0.277  91.69   3.878  0.226    0.677              site8  /path/to/file.bam...
E21294149D  C         T     chrom1  14408     613       86.46       True  1      74     0      530    8       0.163  12.072  0.0    86.46   1.305  0.278    0.275              site8  /path/to/file.bam...
E21294149D  C         T     chrom1  16466     199       90.452      True  1      15     1      180    2       0.503  7.538   0.503  90.452  1.005  0.239    0.529              site8  /path/to/file.bam...
E21294149D  C         T     chrom1  19220     124       99.194      True  0      1      0      123    0       0.0    0.806   0.0    99.194  0.0    0.029    0.0                site8  /path/to/file.bam...
E21294149D  C         T     chrom1  21846     516       94.961      True  2      7      6      490    11      0.388  1.357   1.163  94.961  2.132  0.163    0.904              site8  /path/to/file.bam...
E21294149D  T         C     chrom1  26767     1351      90.6        True  10     1224   5      33     79      0.74   90.6    0.37   2.443   5.848  0.251    0.702              site8  /path/to/file.bam...
E21294149D  T         C     chrom1  27638     110       91.818      True  0      101    1      4      4       0.0    91.818  0.909  3.636   3.636  0.225    0.696              site8  /path/to/file.bam...
E21294149D  C         T     chrom1  27752     145       92.414      True  2      3      2      134    4       1.379  2.069   1.379  92.414  2.759  0.23     0.968              site8  /path/to/file.bam...
```

## Delete data from a project
```
$ vafdb delete example_project E21294149D
<[200] OK>
{
    "project" : "example_project",
    "sample_id": "E21294149D",
    "deleted": true
}
