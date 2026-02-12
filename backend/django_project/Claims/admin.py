# backend/django_project/apps/claims/admin.py
from django.contrib import admin
from .models import Insured, Claim, FraudAlert


@admin.register(Insured)
class InsuredAdmin(admin.ModelAdmin):
    list_display = ['national_code', 'full_name', 'phone_number', 'created_at']
    search_fields = ['national_code', 'full_name', 'phone_number']
    list_filter = ['created_at']
    readonly_fields = ['created_at']


class FraudAlertInline(admin.StackedInline):
    model = FraudAlert
    extra = 1  # تعداد فرم‌های خالی
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