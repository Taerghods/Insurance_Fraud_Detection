# backend/django_project/claims/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_save, post_delete


class ClaimsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'claims'

    def ready(self):
        from .signals import sync_insured_to_neo4j
        Insured = self.get_model('Insured')
        post_save.connect(sync_insured_to_neo4j, sender=Insured)
        post_delete.connect(sync_insured_to_neo4j, sender=Insured)