"""
test_whatsapp_escalation.py — Test Advanced WhatsApp Features
Verifies qualification, CEO alerts, and VAPI callback triggers.
"""

import unittest
from unittest.mock import patch, MagicMock
from lib.retention_client import handle_whatsapp_inbound

class TestWhatsAppEscalation(unittest.TestCase):

    @patch('lib.retention_client.get_all_tenants')
    @patch('lib.whatsapp_agent._get_ai_response')
    @patch('lib.retention_client.send_whatsapp')
    @patch('lib.whatsapp_agent.send_whatsapp')
    @patch('lib.airtable_client.log_whatsapp_message')
    @patch('lib.vapi_client.make_outbound_call')
    def test_whatsapp_qualification_and_callback(self, mock_call, mock_log, mock_wa_send, mock_ret_send, mock_ai, mock_tenants):
        # 1. Setup Mock Tenant
        mock_tenant = MagicMock()
        mock_tenant.whatsapp_number = "+441234567890"
        mock_tenant.client_name = "Gromatic"
        mock_tenant.industry = "Legal"
        mock_tenant.client_id = "gromatic"
        mock_tenant.airtable_base_id = "base_gromatic"
        mock_tenant.vapi_assistant_id = "asst_123"
        mock_tenant.ceo_phone = "whatsapp:+447847221722"

        mock_tenants.return_value = [mock_tenant]

        # 2. Mock AI Response with Qualification Tag
        # Claude hallucinates this tag as per our system prompt instructions
        mock_ai.return_value = "I can certainly help you with that! [QUALIFIED: name=John Doe | need=hiring housing lawyer | book=yes]"

        # 3. Test Message 1: Qualification
        from_num = "whatsapp:+447700900000"
        to_num = "whatsapp:+441234567890"

        reply = handle_whatsapp_inbound(from_num, to_num, "I need a housing lawyer.")

        # Check reply is clean
        self.assertEqual(reply, "I can certainly help you with that!")

        # Check customer reply was sent
        mock_ret_send.assert_called_once()

        # Check CEO was alerted
        mock_wa_send.assert_called_once()
        ceo_call = mock_wa_send.call_args_list[0]
        self.assertEqual(ceo_call[0][0], "whatsapp:+447847221722")
        self.assertIn("Hot lead", ceo_call[0][1])

        # 4. Test Message 2: Callback Request
        mock_ai.return_value = "Sure, I will arrange a call for you."
        mock_call.return_value = {"id": "call_999"}

        reply2 = handle_whatsapp_inbound(from_num, to_num, "Can you call me now?")

        # Check VAPI was triggered
        mock_call.assert_called_once()
        call_kwargs = mock_call.call_args[1]
        self.assertEqual(call_kwargs['phone_number'], "+447700900000")
        self.assertEqual(call_kwargs['assistant_id'], "asst_123")

        # Check reply acknowledged the call
        self.assertIn("calling you now", reply2.lower())

        print("\n✅ WhatsApp Escalation & Qualification Test Passed!")

if __name__ == "__main__":
    unittest.main()
