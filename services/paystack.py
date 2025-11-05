from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction
from django.conf import settings
from django.urls import reverse
import hmac
import hashlib
import json

class PaystackService:
    def __init__(self):
        self.paystack = Paystack(secret_key=settings.PAYSTACK_SECRET_KEY)
    
    def initialize_payment(self, transaction):
        """Initialize payment with Paystack"""
        try:
            
            total_amount = float(transaction.product_price) + float(transaction.logistics_fee)
            # Convert to kobo (multiply by 100)
            amount_in_kobo = int(total_amount * 100)
            
            data = {
                'email': transaction.buyer_email or 'buyer@example.com',
                'amount': amount_in_kobo,
                'reference': str(transaction.id),  
                'callback_url': f"{settings.SITE_URL}/paystack/callback/",
                'metadata': {
                    'transaction_id': str(transaction.id),
                    'product_name': transaction.product_name,
                    'seller_id': transaction.seller.id,
                    'product_price': float(transaction.product_price),
                    'logistics_fee': float(transaction.logistics_fee),
                }
            }
            
            response = Transaction.initialize(**data)
            
            if response['status']:
                return {
                    'success': True,
                    'authorization_url': response['data']['authorization_url'],
                    'access_code': response['data']['access_code'],
                    'reference': response['data']['reference']
                }
            else:
                return {
                    'success': False,
                    'message': response.get('message', 'Payment initialization failed')
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error initializing payment: {str(e)}'
            }
    
    def verify_payment(self, reference):
        """Verify payment with Paystack"""
        try:
            response = Transaction.verify(reference=reference)
            
            if response['status'] and response['data']['status'] == 'success':
                return {
                    'success': True,
                    'data': response['data']
                }
            else:
                return {
                    'success': False,
                    'message': 'Payment verification failed'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error verifying payment: {str(e)}'
            }
    
    def verify_webhook_signature(self, payload, signature):
        """Verify webhook signature for security"""
        if not settings.PAYSTACK_WEBHOOK_SECRET:
            return True  # Skip verification if no secret is set
            
        expected_signature = hmac.new(
            settings.PAYSTACK_WEBHOOK_SECRET.encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)