"""
Django management command to wait for database to be available.
Useful for deployment scenarios where DB might not be immediately ready.
"""
import time
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to pause execution until database is available"""
    
    help = 'Wait for database to be available'

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        retries = 0
        max_retries = 30
        
        while retries < max_retries:
            try:
                db_conn = connection.ensure_connection()
                self.stdout.write(self.style.SUCCESS('Database available!'))
                return
            except OperationalError as e:
                retries += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'Database unavailable (attempt {retries}/{max_retries}): {e}'
                    )
                )
                if retries < max_retries:
                    time.sleep(2)  # Wait 2 seconds before retry
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Database connection failed after {max_retries} attempts'
                        )
                    )
                    raise
