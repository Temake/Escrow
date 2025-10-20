from django.contrib import admin
from .models import Seller, EscrowTransaction

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'created_at']
    search_fields = ['user__username', 'phone']

@admin.register(EscrowTransaction)
class EscrowTransactionAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'seller', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['product_name', 'seller__user__username']
    readonly_fields = ['id', 'created_at', 'paid_at', 'confirmed_at']
