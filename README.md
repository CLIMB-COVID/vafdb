# `vafdb`

## Generating data
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
$ vafdb tsv-create metadata.tsv
<[200] OK>
{
    "sample_id": "E21294149D",
    "task_id": "f13e7d1b-b4f6-40fd-890f-b100ca5b27ee"
}
<[200] OK>
{
    "sample_id": "5523DEB355",
    "task_id": "ed9ba54b-e1a6-4613-b8f9-12a295544943"
}
<[200] OK>
{
    "sample_id": "FE3B496871",
    "task_id": "a77bbf24-f243-498f-938b-d8c8db7ba3ab"
}
<[200] OK>
{
    "sample_id": "E2A89A963D",
    "task_id": "851bf18c-53e6-4f47-90be-191f0d8aa976"
}
<[200] OK>
{
    "sample_id": "99508919E2",
    "task_id": "88aa7765-847d-437c-abe1-744114577ebb"
}
...
```

## Retrieving data
```python
# script.py

from vafdb import Client, utils, Field

# Initialise client
client = Client()

# Create a query
query = (
    Field(reference="MN908947.3")
    & Field(sample_id="E21294149D")
    & (
        (Field(ref_base="C") & Field(base="T"))
        | (Field(ref_base="T") & Field(base="C"))
    )
    & Field(confidence__gt=70)
    & Field(coverage__gt=50)
)

# Send the query to the database
responses = client.query(query)

# Create a pandas dataframe from the result
df = utils.pandafy(responses)

# Print the result in tsv format
print(df.to_csv(index=False, sep="\t"), end="")

```
```
$ python script.py
sample_id   ref_base  base  reference   position  coverage  confidence  diff  num_a  num_c  num_g  num_t  num_ds  pc_a   pc_c    pc_g   pc_t    pc_ds  entropy  secondary_entropy  site   bam_path                   
E21294149D  C         T     MN908947.3  10029     361       91.69       True  1      14     1      331    14      0.277  3.878   0.277  91.69   3.878  0.226    0.677              site8  /path/to/file.bam...
E21294149D  C         T     MN908947.3  14408     613       86.46       True  1      74     0      530    8       0.163  12.072  0.0    86.46   1.305  0.278    0.275              site8  /path/to/file.bam...
E21294149D  C         T     MN908947.3  16466     199       90.452      True  1      15     1      180    2       0.503  7.538   0.503  90.452  1.005  0.239    0.529              site8  /path/to/file.bam...
E21294149D  C         T     MN908947.3  19220     124       99.194      True  0      1      0      123    0       0.0    0.806   0.0    99.194  0.0    0.029    0.0                site8  /path/to/file.bam...
E21294149D  C         T     MN908947.3  21846     516       94.961      True  2      7      6      490    11      0.388  1.357   1.163  94.961  2.132  0.163    0.904              site8  /path/to/file.bam...
E21294149D  T         C     MN908947.3  26767     1351      90.6        True  10     1224   5      33     79      0.74   90.6    0.37   2.443   5.848  0.251    0.702              site8  /path/to/file.bam...
E21294149D  T         C     MN908947.3  27638     110       91.818      True  0      101    1      4      4       0.0    91.818  0.909  3.636   3.636  0.225    0.696              site8  /path/to/file.bam...
E21294149D  C         T     MN908947.3  27752     145       92.414      True  2      3      2      134    4       1.379  2.069   1.379  92.414  2.759  0.23     0.968              site8  /path/to/file.bam...
```