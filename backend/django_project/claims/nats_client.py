# backend/django_project/claims/nats_client.py
import asyncio
import json
import nats
from django.conf import settings


class NATSClient:
    """Send and receive events with NATS"""

    def __init__(self):
        self.nc = None
        self.server = getattr(settings, 'NATS_URL', 'nats://nats:4222')

    async def connect(self):
        """Connect to NATS """
        try:
            self.nc = await nats.connect(self.server)
            print("✅ Connected to NATS")
            return True
        except Exception as e:
            print(f"❌ NATS connection failed: {e}")
            return False

    async def close(self):
        """Close connection"""
        if self.nc:
            await self.nc.close()
            print("NATS connection closed")

    async def publish_fraud_alert(self, claim_id, fraud_score, signals):
        """Send a fraud alert"""
        if not self.nc:
            await self.connect()

        data = {
            "claim_id": claim_id,
            "fraud_score": fraud_score,
            "signals": signals,
            "timestamp": str(asyncio.get_event_loop().time()),
            "severity": "high" if fraud_score >= 70 else "medium" if fraud_score >= 30 else "low"
        }

        await self.nc.publish(
            "fraud.alert",
            json.dumps(data).encode()
        )
        print(f"Fraud alert published: {claim_id}")

    async def subscribe_fraud_alerts(self):
        """Listen to fraud alerts"""
        if not self.nc:
            await self.connect()

        async def message_handler(msg):
            subject = msg.subject
            reply = msg.reply
            data = json.loads(msg.data.decode())
            print(f"📬 Received: {subject} - {data}")

            if data.get('severity') == 'high':
                print(f"CRITICAL: Fraud alert for claim {data['claim_id']}")

        await self.nc.subscribe("fraud.alert", cb=message_handler)
        print("Listening for fraud alerts...")
        await asyncio.Event().wait()