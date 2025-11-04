import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management import BaseCommand

def wait_for_db():
    db_conn = None
    while not db_conn:
        try:
            db_conn = connections['default']
            db_conn.cursor()
        except OperationalError:
            print(" Waiting for the database to be ready...")
            time.sleep(2)
        else:
            print(" Database is ready!")

if __name__ == "__main__":
    wait_for_db()
