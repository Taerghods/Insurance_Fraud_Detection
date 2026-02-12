from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator, MinValueValidator


class Insured(models.Model):
    national_code = models.CharField(max_length=10, validators=[MinLengthValidator(10), MaxLengthValidator(10)], unique=True)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=13, db_index=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['national_code', 'phone_number']),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.national_code}"


class Claim(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('approved', 'تأیید'),
        ('rejected', 'رد'),
        ('fraud', 'مشکوک به تقلب'),
    ]

    insured = models.ForeignKey(Insured, on_delete=models.PROTECT, related_name='claims')   #نمی‌توان بیمه‌شده‌ای را که خسارت دارد حذف کرد
    claim_number = models.CharField(max_length=20, unique=True, blank=True)
    amount = models.IntegerField(validators=[MinValueValidator(0)], help_text="مبلغ به ریال")
    accident_date = models.DateField()
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # Fraud detection
    fraud_score = models.FloatField(default=0, db_index=True)
    fraud_signals = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['insured', 'accident_date']),
            models.Index(fields=['claim_number']),
            models.Index(fields=['status', 'fraud_score']),
        ]

    @property
    def formatted_amount(self):
        """نمایش مبلغ با جداکننده هزارگان"""
        return f"{self.amount:,}".replace(",", ".")

    def __str__(self):
        return self.claim_number or str(self.id)

    def save(self, *args, **kwargs):
        if not self.claim_number:
            last = Claim.objects.count() + 1
            self.claim_number = f"CL-{last:06d}"     #فرمت: CL-000001 (۶ رقم با صفر)
        super().save(*args, **kwargs)


class FraudAlert(models.Model):
    claim = models.OneToOneField(Claim, on_delete=models.CASCADE, related_name='alert')
    fraud_score = models.FloatField(null=True, blank=True, default=0.0)
    signals = models.JSONField(default=list)
    is_resolved = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert: {self.claim.claim_number} - Score: {self.fraud_score}"