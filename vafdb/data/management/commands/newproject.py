from django.core.management import base
from ...models import Project, Reference
from Bio import SeqIO
from maptide import parse_region


class Command(base.BaseCommand):
    help = "Add a new project."

    def add_arguments(self, parser):
        parser.add_argument("code")
        parser.add_argument(
            "--references",
            required=True,
            help="Path of FASTA file containing reference sequence(s).",
        )
        parser.add_argument("--description", help="[optional] Project description.")
        parser.add_argument(
            "--region",
            help="[optional] Specific region to store. Enter in 'CHROM:START-END' format. Default: All regions",
        )
        parser.add_argument(
            "--base-quality",
            type=int,
            default=0,
            help="[optional] Minimum base quality for storing a VAF. Default: 0",
        )
        parser.add_argument(
            "--mapping-quality",
            type=int,
            default=0,
            help="[optional] Minimum mapping quality for storing a VAF. Default: 0",
        )
        parser.add_argument(
            "--min-coverage",
            type=float,
            default=0,
            help="[optional] Minimum coverage for storing a VAF. Default: 0",
        )
        parser.add_argument(
            "--min-entropy",
            type=float,
            default=0,
            help="[optional] Minimum entropy for storing a VAF. Default: 0",
        )
        parser.add_argument(
            "--min-secondary-entropy",
            type=float,
            default=0,
            help="[optional] Minimum secondary entropy for storing a VAF. Default: 0",
        )
        parser.add_argument(
            "--insertions",
            action="store_true",
            help="[optional] Store insertion VAFs. Default: False",
        )
        parser.add_argument(
            "--diff-confidence",
            type=float,
            help="[optional] Only store VAFs with a different base from the reference, above a certain confidence. Default: None",
        )

    def handle(self, *args, **options):
        if options["region"]:
            parse_region(options["region"])

        project = Project.objects.create(
            code=options["code"],
            description=options["description"],
            region=options["region"],
            base_quality=options["base_quality"],
            mapping_quality=options["mapping_quality"],
            min_coverage=options["min_coverage"],
            min_entropy=options["min_entropy"],
            min_secondary_entropy=options["min_secondary_entropy"],
            insertions=options["insertions"],
            diff_confidence=options["diff_confidence"],
        )

        references = []
        for fasta in SeqIO.parse(open(options["references"]), "fasta"):
            name, sequence = fasta.id, str(fasta.seq)
            print(f"Reference name: {name}")
            print(f"Sequence length: {len(sequence)}")
            yn = input("Rename this reference? [y/n]: ").upper()

            n = ""
            if yn == "Y":
                while not n:
                    n = input("Reference name: ").upper()
            name = n

            yn = input("Proceed? [y/n]: ").upper()
            if yn == "Y":
                Reference.objects.create(project=project, name=name, sequence=sequence)
                print(
                    f"Reference sequence for project '{options['code']}' added to the database."
                )
                references.append(name)
            else:
                print("Sequence ignored.")

        print("Project created.")
        print("Code:", project.code)
        print("Description:", project.description)
        print("Reference sequences:", references)
