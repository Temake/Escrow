from django.db import models
from django.contrib.auth.models import User
import uuid
from decimal import Decimal

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    bank_account = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.phone}"

class EscrowTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid - Awaiting Confirmation'),
        ('confirmed', 'Confirmed'),
        ('refunded', 'Refunded'),
    ]
    
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
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    @property
    def total_amount(self):
        return self.product_price + self.logistics_fee
    
    def __str__(self):
        return f"{self.product_name} - {self.status}"
