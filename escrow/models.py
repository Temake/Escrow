from django.db import models
from django.contrib.auth.models import User
import uuid
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    bank_account = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.phone}"
    
    @property
    def total_earnings(self):
        """Calculate total confirmed earnings"""
        confirmed = self.escrowtransaction_set.filter(status='confirmed')
        return sum(t.seller_amount for t in confirmed)

class EscrowTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid - Awaiting Confirmation'),
        ('confirmed', 'Confirmed'),
        ('refunded', 'Refunded'),
        ('expired', 'Expired - Auto Refund'),
    ]
    
    PLATFORM_FEE_PERCENT = Decimal('2.5')  # 2.5% platform fee
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    
    # Product details
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    logistics_fee = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Buyer details
    buyer_phone = models.CharField(max_length=15, blank=True)
    buyer_email = models.EmailField(blank=True)
    
    # Transaction status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    confirmation_code = models.CharField(max_length=10, blank=True)
    
    # Payment tracking
    paystack_reference = models.CharField(max_length=100, blank=True)
    logistics_released = models.BooleanField(default=False)
    product_released = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    
    @property
    def total_amount(self):
        """Total amount buyer pays"""
        return self.product_price + self.logistics_fee
    
    @property
    def platform_fee(self):
        """Platform fee (2.5% of product price only)"""
        return (self.product_price * self.PLATFORM_FEE_PERCENT / 100).quantize(Decimal('0.01'))
    
    @property
    def seller_amount(self):
        """Amount seller receives after platform fee"""
        return self.product_price - self.platform_fee
    
    @property
    def is_expired(self):
        """Check if transaction has passed deadline"""
        if self.deadline and timezone.now() > self.deadline:
            return True
        return False
    
    def set_deadline(self):
        """Set deadline to 2 days + 1 day grace from payment"""
        if self.paid_at:
            self.deadline = self.paid_at + timedelta(days=3)
            self.save()
    
    def __str__(self):
        return f"{self.product_name} - {self.status}"
