import time
from django.db import connections
from django.db.utils import OperationalError

def wait_for_db():
    while True:
        try:
            connections['default'].cursor()
            print("✅ Database is ready!")
            break
        except OperationalError:
            print("🕒 Waiting for database to be ready...")
            time.sleep(2)

if __name__ == "__main__":
    wait_for_db()
