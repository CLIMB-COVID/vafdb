from django.core.management import base
from ...models import Project


class Command(base.BaseCommand):
    help = "Delete a project."

    def add_arguments(self, parser):
        parser.add_argument("code")

    def handle(self, *args, **options):
        project = Project.objects.get(code=options["code"])
        print(
            "WARNING: Deleting this project will delete all metadata and VAFs associated with it."
        )
        yn = input("Proceed? [y/n]:").upper()

        if yn == "Y":
            project.delete()
            print("Project deleted.")
