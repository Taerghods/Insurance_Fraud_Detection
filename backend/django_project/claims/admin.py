# backend/django_project/apps/claims/admin.py
from django.contrib import admin
from django.utils.html import format_html

from .models import Insured, Claim, FraudAlert


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
    list_display = ['claim_number', 'insured', 'formatted_amount', 'status', 'fraud_score', 'created_at']
    list_filter = ['status', 'accident_date', 'fraud_score']
    search_fields = ['claim_number', 'insured__national_code', 'insured__full_name']
    readonly_fields = ['claim_number', 'fraud_score', 'fraud_signals', 'created_at']
    fieldsets = (
        ('اطلاعات خسارت', {'fields': ('insured', 'amount', 'accident_date', 'description')}),
        ('وضعیت', {'fields': ('status', 'fraud_score', 'fraud_signals'),}),
    )
    inlines = [FraudAlertInline]

    def formatted_amount(self, obj):
        return obj.formatted_amount
    formatted_amount.short_description = 'مبلغ'

    def colored_fraud_score(self, obj):
        """نمایش رنگی امتیاز تقلب"""
        score = obj.fraud_score
        if score >= 70:
            color = 'red'
            text = '⚠️ خطرناک'
        elif score >= 30:
            color = 'orange'
            text = '⚡ مشکوک'
        else:
            color = 'green'
            text = '✓ عادی'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} - {}</span>',
            color, score, text
        )

    colored_fraud_score.short_description = 'امتیاز تقلب'


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

    colored_fraud_score.short_description = 'امتیاز'