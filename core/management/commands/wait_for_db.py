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
        max_retries = 60  # Increased for SSL stability
        
        while retries < max_retries:
            try:
                # Close any existing connection first to force fresh connection
                connection.close()
                db_conn = connection.ensure_connection()
                self.stdout.write(self.style.SUCCESS('Database available!'))
                return
            except OperationalError as e:
                retries += 1
                # Exponential backoff with jitter for SSL issues
                wait_time = min(2 * (1.5 ** (retries // 10)), 10)  # Cap at 10 seconds
                
                self.stdout.write(
                    self.style.WARNING(
                        f'Database unavailable (attempt {retries}/{max_retries}): {str(e)[:100]}'
                    )
                )
                if retries < max_retries:
                    self.stdout.write(f'  Retrying in {wait_time:.1f} seconds...')
                    time.sleep(wait_time)
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Database connection failed after {max_retries} attempts'
                        )
                    )
                    raise
