"""
test_whatsapp_flow.py — Test WhatsApp Inbound Flow
Mocks Twilio, Claude, and Airtable to verify the logic in lib/retention_client.py.
"""

import unittest
from unittest.mock import patch, MagicMock
from lib.retention_client import handle_whatsapp_inbound

class TestWhatsAppFlow(unittest.TestCase):

    @patch('lib.retention_client.get_all_tenants')
    @patch('lib.retention_client.claude_client.messages.create')
    @patch('lib.retention_client.send_whatsapp')
    @patch('lib.airtable_client.log_whatsapp_message')
    def test_handle_whatsapp_inbound_success(self, mock_log, mock_send, mock_claude, mock_tenants):
        # 1. Setup Mock Tenant
        mock_tenant = MagicMock()
        mock_tenant.whatsapp_number = "+441234567890"
        mock_tenant.client_name = "Test Client"
        mock_tenant.industry = "Testing"
        mock_tenant.client_id = "test_client_id"
        mock_tenant.airtable_base_id = "test_base_id"
        mock_tenant.calcom_event_type_id = "test_cal_link"

        mock_tenants.return_value = [mock_tenant]

        # 2. Setup Mock Claude Response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Hello! How can I help you today?")]
        mock_claude.return_value = mock_response

        # 3. Setup Mock Airtable Response
        mock_log.return_value = {"id": "rec123"}

        # 4. Execute Handler
        from_num = "whatsapp:+447700900000"
        to_num = "whatsapp:+441234567890"
        body = "Hi, I need help with testing."

        reply = handle_whatsapp_inbound(from_num, to_num, body)

        # 5. Assertions
        self.assertEqual(reply, "Hello! How can I help you today?")

        # Verify Claude was called with the right prompt
        mock_claude.assert_called_once()
        args, kwargs = mock_claude.call_args
        self.assertIn("Test Client", kwargs['system'])
        self.assertEqual(kwargs['messages'][0]['content'], body)

        # Verify WhatsApp was sent back
        mock_send.assert_called_once_with("+447700900000", reply, from_number=to_num)

        # Verify Airtable was logged
        mock_log.assert_called_once_with(
            base_id="test_base_id",
            client_id="test_client_id",
            sender_phone=from_num,
            message_content=body,
            response_content=reply,
            lead_score=0
        )

        print("\n✅ WhatsApp Flow Test Passed!")

    @patch('lib.retention_client.get_all_tenants')
    def test_handle_whatsapp_inbound_no_tenant(self, mock_tenants):
        mock_tenants.return_value = []

        reply = handle_whatsapp_inbound("whatsapp:+1", "whatsapp:+2", "hello")

        self.assertEqual(reply, "Business not found.")
        print("✅ No Tenant Test Passed!")

if __name__ == "__main__":
    unittest.main()
