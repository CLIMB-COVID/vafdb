from django.core.management import base
from django.db.utils import IntegrityError
from ...models import Reference
from Bio import SeqIO


class Command(base.BaseCommand):
    help = "Create reference sequences in the database."

    def add_arguments(self, parser):
        parser.add_argument("fasta")

    def handle(self, *args, **options):
        for fasta in SeqIO.parse(open(options["fasta"]), "fasta"):
            name, sequence = fasta.id, str(fasta.seq)
            print(f"Name: {name}")
            print(f"Sequence length: {len(sequence)}")
            yn = input("Proceed? [y/n]: ").upper()
            if yn == "Y":
                try:
                    Reference.objects.create(name=name, sequence=sequence)
                    print("Reference sequence added to the database.")
                except IntegrityError:
                    yn = input(
                        f"{name} already exists in the database. Do you want to overwrite its sequence? [y/n]: "
                    ).upper()
                    if yn == "Y":
                        ref = Reference.objects.get(name=name)
                        ref.sequence = sequence
                        ref.save(update_fields=["sequence"])
                        print("Reference sequence updated.")
                    else:
                        print("Sequence ignored.")

            else:
                print("Sequence ignored.")
