# backend/django_project/claims/management/commands/sync_neo4j.py
from django.core.management.base import BaseCommand
from backend.django_project.claims.services import sync_all_to_neo4j


class Command(BaseCommand):
    help = 'Sync all Insured data from PostgreSQL to Neo4j'

    def handle(self, *args, **options):
        sync_all_to_neo4j()
        self.stdout.write(self.style.SUCCESS('✅ Neo4j sync completed!'))