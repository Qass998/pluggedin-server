"""Railway-safe worker and cron commands backed by Postgres."""

from __future__ import annotations

import argparse
import os
import time
from uuid import UUID

from .core import AcceptanceFixtureProvider, Prime
from .repository import PostgresRepository


def enqueue(tenant_id: str, desk: str, mode: str = "live") -> str:
    UUID(tenant_id)
    repo = PostgresRepository()
    repo.ensure_tenant(tenant_id)
    with repo.connection() as connection, connection.cursor() as cursor:
        cursor.execute("INSERT INTO agent_jobs (tenant_id,desk,mode) VALUES (%s,%s,%s) RETURNING id", (tenant_id, desk, mode))
        return str(cursor.fetchone()[0])


def claim_and_run() -> bool:
    repo = PostgresRepository()
    with repo.connection() as connection, connection.cursor() as cursor:
        cursor.execute("SELECT id,tenant_id,desk,mode FROM agent_jobs WHERE status='queued' AND available_at<=now() ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1")
        job = cursor.fetchone()
        if not job:
            return False
        cursor.execute("UPDATE agent_jobs SET status='running',locked_at=now(),attempts=attempts+1 WHERE id=%s", (job[0],))
    job_id, tenant_id, desk, mode = map(str, job)
    try:
        if mode != "acceptance":
            raise RuntimeError("No live source adapter is enabled; refusing to substitute fixture data")
        provider = AcceptanceFixtureProvider()
        Prime(provider, provider, provider, repo).run(tenant_id, desk, 1, 1)
        with repo.connection() as connection, connection.cursor() as cursor:
            cursor.execute("UPDATE agent_jobs SET status='completed',completed_at=now() WHERE id=%s", (job_id,))
    except Exception as error:
        with repo.connection() as connection, connection.cursor() as cursor:
            cursor.execute("UPDATE agent_jobs SET status='failed',last_error=%s WHERE id=%s", (str(error), job_id))
    return True


def worker(poll_seconds: int = 5) -> None:
    while True:
        if not claim_and_run():
            time.sleep(poll_seconds)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    worker_parser = sub.add_parser("worker")
    worker_parser.add_argument("--poll-seconds", type=int, default=5)
    enqueue_parser = sub.add_parser("enqueue")
    enqueue_parser.add_argument("--tenant", default=os.environ.get("PLUGGEDIN_TENANT_ID", ""))
    enqueue_parser.add_argument("--desk", required=True, choices=("agri_food", "industrial_distribution", "construction_supply"))
    enqueue_parser.add_argument("--mode", default="live", choices=("live", "acceptance"))
    args = parser.parse_args()
    if args.command == "worker":
        worker(args.poll_seconds)
    else:
        print(enqueue(args.tenant, args.desk, args.mode))


if __name__ == "__main__":
    main()
