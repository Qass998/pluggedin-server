import os
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

from api.deal_server import identity
from deal_os.repository import COMMUNICATION_STATES


class DealAPIContractTest(unittest.TestCase):
    def test_internal_bearer_and_tenant_are_required(self):
        with patch.dict(os.environ, {"PLUGGEDIN_INTERNAL_API_KEY": "correct"}):
            self.assertEqual(identity("Bearer correct", "00000000-0000-0000-0000-000000000001"), "00000000-0000-0000-0000-000000000001")
            with self.assertRaises(HTTPException) as wrong:
                identity("Bearer wrong", "00000000-0000-0000-0000-000000000001")
            self.assertEqual(wrong.exception.status_code, 401)
            with self.assertRaises(HTTPException) as missing_tenant:
                identity("Bearer correct", "")
            self.assertEqual(missing_tenant.exception.status_code, 400)

    def test_communication_funnel_covers_introduction_and_commercial_progression(self):
        for state in ("contact_approved", "contacted", "replied", "both_interested", "introduction_approved", "introduced", "negotiating", "commercially_progressing", "won", "lost"):
            self.assertIn(state, COMMUNICATION_STATES)

    def test_railway_runtime_fails_closed_without_live_source_adapter(self):
        worker = Path("deal_os/jobs.py").read_text(encoding="utf-8")
        self.assertIn("No live source adapter is enabled", worker)
        self.assertIn("FOR UPDATE SKIP LOCKED", worker)
        self.assertNotIn("send_email", worker)
        self.assertNotIn("send_whatsapp", worker)

    def test_schema_is_tenant_scoped_and_tracks_communication_approvals(self):
        schema = Path("deal_os/schema.sql").read_text(encoding="utf-8")
        for table in ("sources", "signals", "needs", "offers", "evidence", "verifications", "matches", "opportunities", "conversations", "deals", "agent_runs", "approval_actions", "agent_jobs"):
            self.assertIn(f"CREATE TABLE {table}", schema)
        self.assertIn("party_side", schema)
        self.assertIn("follow_up_at", schema)
        self.assertIn("conversations_approval_fk", schema)


if __name__ == "__main__":
    unittest.main()
