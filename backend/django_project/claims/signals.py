# backend/django_project/claims/signals.py
import asyncio
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Insured, Claim, FraudAlert
from .nats_client import NATSClient
from .services import Neo4jClient


# ================ Insured Signals ================
@receiver(post_save, sender=Insured)
def sync_insured_to_neo4j(sender, instance, created, **kwargs):
    """Sync Insured to Neo4j when saved"""
    neo4j = Neo4jClient()
    neo4j.create_insured_node(instance)
    neo4j.close()
    action = "Created" if created else "Updated"
    print(f"{action}: {instance.full_name} synced to Neo4j")


@receiver(post_delete, sender=Insured)
def delete_insured_from_neo4j(sender, instance, **kwargs):
    """Delete Insured from Neo4j when removed"""
    neo4j = Neo4jClient()
    with neo4j.driver.session() as session:
        session.run("MATCH (i:Insured {id: $id}) DETACH DELETE i", id=instance.id)
    neo4j.close()
    print(f"{instance.full_name} deleted from Neo4j")


# ================ Claim Signals ================
@receiver(pre_save, sender=Claim)
def calculate_fraud_score(sender, instance, **kwargs):
    """Calculate fraud score before saving Claim"""
    if instance.insured_id:
        neo4j = Neo4jClient()
        instance.fraud_score = neo4j.get_fraud_score(instance.insured_id)
        neo4j.close()
        print(f"Fraud score for {instance.claim_number}: {instance.fraud_score}")


@receiver(post_save, sender=Claim)
def create_fraud_alert_and_notify(sender, instance, created, **kwargs):
    """Create fraud alert and send NATS notification for high-risk claims"""
    if instance.fraud_score >= 30 and not hasattr(instance, 'alert'):
        # Create FraudAlert in database
        alert = FraudAlert.objects.create(
            claim=instance,
            fraud_score=instance.fraud_score,
            signals=[f"Fraud score: {instance.fraud_score}"]
        )
        print(f"🚨 Fraud alert created for {instance.claim_number}")

        # Send NATS notification
        try:
            nats_client = NATSClient()
            asyncio.run(nats_client.connect())
            asyncio.run(nats_client.publish_fraud_alert(
                claim_id=instance.id,
                fraud_score=instance.fraud_score,
                signals=["Duplicate phone number" if instance.fraud_score >= 30 else "Duplicate address"]
            ))
            asyncio.run(nats_client.close())
        except Exception as e:
            print(f"⚠️ NATS notification failed: {e}")


# ================ Fraud Alert Signals ================
@receiver(post_save, sender=Claim)
def create_fraud_alert(sender, instance, created, **kwargs):
    """ایجاد خودکار هشدار تقلب برای claims با امتیاز بالا"""
    if instance.fraud_score >= 30:  # آستانه تقلب
        # اگه از قبل هشدار نداره، بساز
        if not hasattr(instance, 'alert'):
            FraudAlert.objects.create(
                claim=instance,
                fraud_score=instance.fraud_score,
                signals=[f"Fraud score: {instance.fraud_score}"]
            )
            print(f"Fraud alert created for {instance.claim_number}")