import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError

class Command(BaseCommand):
    """Django command to pause execution until database is available"""
    
    help = 'Wait for database to be available'

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=60,
            help='Maximum time to wait for database (seconds)'
        )

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        timeout = options['timeout']
        start_time = time.time()
        db_conn = None
        
        while not db_conn:
            try:
                db_conn = connections['default']
                with db_conn.cursor() as cursor:
                    cursor.execute('SELECT 1')
                break
            except OperationalError:
                if time.time() - start_time > timeout:
                    self.stderr.write(
                        self.style.ERROR(
                            f'❌ Database connection timeout after {timeout} seconds'
                        )
                    )
                    raise
                self.stdout.write('⏳ Database unavailable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('✅ Database available!'))
