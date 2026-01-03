from django.core.management import BaseCommand
from django.db import connections, OperationalError
import time


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Waiting for db connection...")

        db_con = None
        while db_con is None:
            try:
                db_con = connections["default"]
                db_con.cursor()
            except OperationalError:
                self.stdout.write(
                    self.style.WARNING(
                        "Database unavailable, trying again..."
                    )
                )
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database connected"))
