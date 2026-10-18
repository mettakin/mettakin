from django.core.management.base import BaseCommand

from members.models import Member


class Command(BaseCommand):
    help = "After a restore, delete again the members who deleted their account since the backup."

    def add_arguments(self, parser):
        parser.add_argument(
            "numbers", nargs="+", type=int, help="Member numbers from the deletion emails"
        )

    def handle(self, *args, numbers, **options):
        members = Member.objects.filter(pk__in=numbers)
        found = sorted(members.values_list("pk", flat=True))
        for member in members:
            member.delete()
        gone = sorted(set(numbers) - set(found))
        self.stdout.write(f"Deleted again: {found or 'none'}. Already gone: {gone or 'none'}.")
