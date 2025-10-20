from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from escrow.forms import UserRegForm
from .models import EscrowTransaction, Seller
import random
import string
from django.contrib.auth import get_user_model

User = get_user_model()


def home(request):
    """Landing page"""
    return render(request, 'escrow/home.html')

@login_required
def create_payment_link(request):
    """Seller creates a payment link"""
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_price = request.POST.get('product_price')
        logistics_fee = request.POST.get('logistics_fee')
        buyer_phone = request.POST.get('buyer_phone', '')
        buyer_email = request.POST.get('buyer_email', '')
  
        seller, created = Seller.objects.get_or_create(
            user=request.user,
            defaults={'phone': request.POST.get('seller_phone', '')}
        )
        
        transaction = EscrowTransaction.objects.create(
            seller=seller,
            product_name=product_name,
            product_price=product_price,
            logistics_fee=logistics_fee,
            buyer_phone=buyer_phone,
            buyer_email=buyer_email
        )
        
        messages.success(request, 'Payment link created successfully!')
        return redirect('payment_link_detail', transaction_id=transaction.id)
    
    return render(request, 'escrow/create_link.html')

def payment_page(request, transaction_id):
    """Buyer payment page"""
    transaction = get_object_or_404(EscrowTransaction, id=transaction_id)
    
    if request.method == 'POST':
        # Simulate payment processing
        # In real implementation, integrate with Paystack/Flutterwave
        
        # Generate confirmation code
        confirmation_code = ''.join(random.choices(string.digits, k=6))
        transaction.confirmation_code = confirmation_code
        transaction.status = 'paid'
        transaction.save()
        
        # In real app, send SMS/email with confirmation code
        messages.success(request, f'Payment successful! Your confirmation code: {confirmation_code}')
        return redirect('payment_success', transaction_id=transaction.id)
    
    return render(request, 'escrow/payment_page.html', {'transaction': transaction})

def payment_success(request, transaction_id):
    """Payment success page with confirmation code"""
    transaction = get_object_or_404(EscrowTransaction, id=transaction_id)
    return render(request, 'escrow/payment_success.html', {'transaction': transaction})

def confirm_delivery(request, transaction_id):
    """Buyer confirms delivery with code"""
    transaction = get_object_or_404(EscrowTransaction, id=transaction_id)
    
    if request.method == 'POST':
        entered_code = request.POST.get('confirmation_code')
        
        if entered_code == transaction.confirmation_code and transaction.status == 'paid':
            transaction.status = 'confirmed'
            transaction.save()
            messages.success(request, 'Delivery confirmed! Payment released to seller.')
            return redirect('confirmation_success')
        else:
            messages.error(request, 'Invalid confirmation code.')
    
    return render(request, 'escrow/confirm_delivery.html', {'transaction': transaction})

def confirmation_success(request):
    """Confirmation success page"""
    return render(request, 'escrow/confirmation_success.html')

@login_required
def payment_link_detail(request, transaction_id):
    """Show payment link details to seller"""
    transaction = get_object_or_404(EscrowTransaction, id=transaction_id)
    
    # Generate shareable payment link
    payment_url = request.build_absolute_uri(f'/pay/{transaction.id}/')
    
    return render(request, 'escrow/payment_link_detail.html', {
        'transaction': transaction,
        'payment_url': payment_url
    })

def SignUp(request):
    if request.method == 'GET':
        return render(request, 'escrow/signup.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
    
        has_error = False
        
        if not username:
            messages.error(request, 'Username cannot be empty.')
            has_error = True
            
        if not email:
            messages.error(request, 'Email cannot be empty.')
            has_error = True
            
        if not password:
            messages.error(request, 'Password cannot be empty.')
            has_error = True
            
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            has_error = True
            
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            has_error = True
            
        if len(password or '') < 6:  
            messages.error(request, 'Password must be at least 6 characters long.')
            has_error = True
      
        if not has_error:
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'User registered successfully!')
            return redirect('home')
    
    return render(request, 'escrow/signup.html')