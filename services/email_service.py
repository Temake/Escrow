from django.core.mail import send_mail
from django.conf import settings

def send_confirmation_code_email(transaction):
    """Send confirmation code to buyer via email"""
    if not transaction.buyer_email:
        return False
    
    subject = f'Your Confirmation Code - {transaction.product_name}'
    
    message = f"""
Hello,

Your payment for {transaction.product_name} was successful!

Your Confirmation Code: {transaction.confirmation_code}

Please keep this code safe. You'll need it to confirm delivery and release payment to the seller.

Product: {transaction.product_name}
Amount Paid: ₦{transaction.total_amount:,.2f}
Deadline: {transaction.deadline.strftime('%B %d, %Y at %I:%M %p') if transaction.deadline else 'N/A'}

To confirm delivery, visit: {settings.SITE_URL}/confirm/{transaction.id}/

Thank you for using our secure escrow service!
"""
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [transaction.buyer_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
