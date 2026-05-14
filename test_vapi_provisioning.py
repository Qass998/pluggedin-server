#!/usr/bin/env python3
"""
Test script: VAPI phone provisioning for Module 1 (Presence Agent)

This demonstrates the complete flow:
1. Create inbound VAPI assistant
2. Provision real phone number
3. Update Airtable with phone details
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import our libraries
from lib import vapi_client, dispatch_client, airtable_client

print("=" * 60)
print("VAPI PHONE PROVISIONING TEST")
print("=" * 60)

# Test data (Gromatic example)
test_client = {
    "client_id": "rec_gromatic_demo",
    "client_name": "Damian @ Gromatic",
    "business_name": "Gromatic",
    "industry": "Legal",
    "cal_link": "https://calendly.com/gromatic/consultation",
    "country": "GB",
    "area_code": "161",  # Manchester
}

print("\n📋 TEST CLIENT:")
print(f"  Business: {test_client['business_name']}")
print(f"  Industry: {test_client['industry']}")
print(f"  Cal Link: {test_client['cal_link']}")

print("\n🚀 PROVISIONING PRESENCE AGENT...")

# Call the provisioning function
result = dispatch_client.provision_presence_agent(
    client_id=test_client["client_id"],
    client_name=test_client["client_name"],
    business_name=test_client["business_name"],
    industry=test_client["industry"],
    cal_link=test_client["cal_link"],
    faqs=[
        {
            "question": "What services do you provide?",
            "answer": "We offer legal services for businesses and individuals."
        },
        {
            "question": "How do I book a consultation?",
            "answer": "Visit our booking link or call during business hours."
        }
    ],
    country=test_client["country"],
    area_code=test_client["area_code"],
)

print("\n✅ RESULT:")
if result.get("status") == "active":
    print(f"  Status: {result['status']}")
    print(f"  Phone ID: {result['phone_number_id']}")
    print(f"  Assistant ID: {result['assistant_id']}")
    print(f"  Message: {result['message']}")
    print(f"  Note: {result['note']}")
else:
    print(f"  Status: {result.get('status', 'unknown')}")
    print(f"  Error: {result.get('error', 'Unknown error')}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

# If successful, show how to use the number
if result.get("status") == "active":
    print("\n📱 CLIENT CAN NOW USE THIS:")
    print(f"   Phone ID: {result['phone_number_id']}")
    print(f"   Status: Active and receiving calls")
    print(f"   Calls automatically route to AI receptionist")
    print(f"   All calls logged to Airtable")
