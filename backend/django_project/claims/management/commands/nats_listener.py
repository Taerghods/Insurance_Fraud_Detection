# backend/django_project/claims/management/commands/nats_listener.py
from django.core.management.base import BaseCommand
import asyncio
from backend.django_project.claims.nats_client import NATSClient


class Command(BaseCommand):
    help = 'Listen to NATS fraud alerts'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting NATS listener'))

        async def listen():
            nats = NATSClient()
            await nats.connect()
            await nats.subscribe_fraud_alerts()

        asyncio.run(listen())