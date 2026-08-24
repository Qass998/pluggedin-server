import unittest

from deal_os.core import AcceptanceFixtureProvider, DESKS, InMemoryRepository, Prime


class DealOSAcceptanceTest(unittest.TestCase):
    def setUp(self):
        self.provider = AcceptanceFixtureProvider()
        self.repository = InMemoryRepository()
        self.prime = Prime(self.provider, self.provider, self.provider, self.repository)

    def test_three_desks_lock_the_300_signal_experiment(self):
        self.assertEqual(set(DESKS), {"agri_food", "industrial_distribution", "construction_supply"})
        self.assertEqual(sum(desk["explicit_signal_target"] for desk in DESKS.values()), 300)

    def test_signal_first_acceptance_flow_surfaces_a_human_review_brief(self):
        result = self.prime.run("pluggedin-internal", "agri_food", 1, 1)
        self.assertEqual(len(result["results"]), 1)
        match = result["results"][0]
        self.assertEqual(match["signal"]["requirement"]["quantity"], "10 MT")
        self.assertEqual(match["counterparty"]["company_name"], "Keitt Exporters Limited")
        self.assertNotEqual(match["signal"]["market"], match["counterparty"]["market"])
        self.assertGreaterEqual(match["score"], 60)
        self.assertEqual(match["stage"], "human_review")
        self.assertIn("Still unverified", match["brief"])

    def test_verifier_does_not_overclaim_public_evidence(self):
        match = self.prime.run("pluggedin-internal", "agri_food", 1, 1)["results"][0]
        self.assertEqual(match["signal_verification"]["status"], "plausible")
        self.assertEqual(match["counterparty_verification"]["status"], "plausible")
        self.assertIn("legal buyer identity", match["signal_verification"]["unknowns"])
        self.assertIn("10 MT availability", match["counterparty_verification"]["unknowns"])

    def test_consequential_action_is_pending_and_has_no_executor(self):
        self.prime.run("pluggedin-internal", "agri_food", 1, 1)
        self.assertEqual(self.repository.approvals[0]["action_type"], "contact_counterparties")
        self.assertEqual(self.repository.approvals[0]["status"], "pending")
        self.assertIn("No outreach executor", self.repository.approvals[0]["note"])


if __name__ == "__main__":
    unittest.main()
