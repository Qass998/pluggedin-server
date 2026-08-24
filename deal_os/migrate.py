"""Apply the initial Deal OS schema once at service startup."""
from pathlib import Path
from .repository import PostgresRepository

def migrate() -> bool:
    repository = PostgresRepository()
    with repository.connection() as connection, connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass('public.tenants')")
        if cursor.fetchone()[0]:
            return False
        cursor.execute(Path(__file__).with_name("schema.sql").read_text())
    return True

if __name__ == "__main__":
    print("schema applied" if migrate() else "schema already present")

