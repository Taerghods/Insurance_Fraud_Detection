# backend/django_project/claims/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Insured, Claim, FraudAlert
from .services import Neo4jClient


@admin.register(Insured)
class InsuredAdmin(admin.ModelAdmin):
    list_display = ['national_code', 'full_name', 'phone_number', 'address', 'created_at']
    search_fields = ['national_code', 'full_name', 'phone_number']
    list_filter = ['created_at']
    readonly_fields = ['created_at']


class FraudAlertInline(admin.StackedInline):
    model = FraudAlert
    extra = 0
    readonly_fields = ['fraud_score', 'signals', 'created_at']
    can_delete = True
    fields = ['fraud_score', 'signals', 'is_resolved', 'created_at']


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['claim_number', 'insured', 'formatted_amount', 'status', 'live_fraud_score', 'created_at']
    list_filter = ['status', 'accident_date']
    search_fields = ['claim_number', 'insured__national_code', 'insured__full_name']
    readonly_fields = ['claim_number', 'fraud_signals', 'created_at', 'live_fraud_score']
    inlines = [FraudAlertInline]

    fieldsets = (
        ('Claim Information', {
            'fields': ('insured', 'amount', 'accident_date', 'description')
        }),
        ('Status', {
            'fields': ('status', 'live_fraud_score', 'fraud_signals'),
        }),
    )

    def formatted_amount(self, obj):
        return obj.formatted_amount
    formatted_amount.short_description = 'Amount'

    def live_fraud_score(self, obj):
        """Get live fraud score from Neo4j without saving to database"""
        # Return gray text if no insured exists
        if not obj.insured_id:
            return format_html('<span style="color: gray;">No Insured</span>')

        try:
            neo4j = Neo4jClient()
            score = neo4j.get_fraud_score(obj.insured_id)
            neo4j.close()
        except Exception as e:
            print(f"⚠️ Neo4j error: {e}")
            score = 0

        if score >= 70:
            color = 'red'
            text = '⚠️ High Risk'
        elif score >= 30:
            color = 'orange'
            text = '⚡ Suspicious'
        else:
            color = 'green'
            text = '✓ Normal'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{} - {}</span>',
            color, score, text
        )
    live_fraud_score.short_description = 'Fraud Score (Live)'


@admin.register(FraudAlert)
class FraudAlertAdmin(admin.ModelAdmin):
    list_display = ['claim', 'colored_fraud_score', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'fraud_score', 'created_at']
    search_fields = ['claim__claim_number', 'claim__insured__national_code']
    readonly_fields = ['fraud_score', 'signals', 'created_at']
    raw_id_fields = ['claim']

    def colored_fraud_score(self, obj):
        score = obj.fraud_score
        if score >= 70:
            color = 'red'
        elif score >= 30:
            color = 'orange'
        else:
            color = 'green'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, score)
    colored_fraud_score.short_description = 'Score'