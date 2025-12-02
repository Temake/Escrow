from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from escrow.forms import UserRegForm
from .models import EscrowTransaction, Seller
import random
import string
from django.contrib.auth import get_user_model
from services.paystack import PaystackService
from services.email_service import send_confirmation_code_email

User = get_user_model()
paystack_service = PaystackService()


def home(request):
    cards= [
        {'title': 'Trust-first checkout', 'copy': 'Crystal clear breakdown (product, logistics, rules) on every link so buyers feel safe instantly.'},
        {'title': 'Escrow lock', 'copy': 'Funds stay in escrow until buyer confirms delivery. No shortcuts. No early withdrawals.'},
        {'title': 'Logistics protected', 'copy': 'Logistics fee releases the moment payment hits, so riders and sellers never lose cash on failed deliveries.'}
    ]
    return render(request, 'escrow/home.html', {'cards': cards})

@login_required
def create_payment_link(request):
    """Seller creates a payment link"""
    # Check if seller profile exists
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        seller = None
    
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_price = request.POST.get('product_price')
        logistics_fee = request.POST.get('logistics_fee')
        buyer_phone = request.POST.get('buyer_phone', '')
        buyer_email = request.POST.get('buyer_email', '')
        
        # Create or update seller profile
        if not seller:
            phone = request.POST.get('seller_phone')
            bank_account = request.POST.get('bank_account')
            bank_name = request.POST.get('bank_name', '')
            
            if not phone or not bank_account:
                messages.error(request, 'Phone and bank account are required for first transaction.')
                return render(request, 'escrow/create_link.html', {'show_seller_form': True})
            
            seller = Seller.objects.create(
                user=request.user,
                phone=phone,
                bank_account=bank_account,
                bank_name=bank_name
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
    
    context = {
        'seller': seller,
        'show_seller_form': seller is None
    }
    return render(request, 'escrow/create_link.html', context)

def payment_page(request, transaction_id):
    """Buyer payment page - initialize Paystack payment"""
    transaction = get_object_or_404(EscrowTransaction, id=transaction_id)
    
    if transaction.status != 'pending':
        messages.info(request, 'This payment link has already been used.')
        return redirect('payment_success', transaction_id=transaction.id)
    
    if request.method == 'POST':
        # Initialize payment with Paystack
        result = paystack_service.initialize_payment(transaction)
        
        if result['success']:
            # Redirect to Paystack payment page
            return redirect(result['authorization_url'])
        else:
            messages.error(request, f"Payment initialization failed: {result['message']}")
    
    context = {
        'transaction': transaction,
    }
    return render(request, 'escrow/payment_page.html', context)

def paystack_callback(request):
    """Handle Paystack payment callback"""
    reference = request.GET.get('reference')
    
    if not reference:
        messages.error(request, 'Invalid payment reference.')
        return redirect('home')
    
    # Verify payment with Paystack
    result = paystack_service.verify_payment(reference)
    
    if result['success']:
        # Get transaction
        transaction = get_object_or_404(EscrowTransaction, id=reference)
        
        # Generate confirmation code
        confirmation_code = ''.join(random.choices(string.digits, k=6))
        
        # Update transaction
        transaction.confirmation_code = confirmation_code
        transaction.status = 'paid'
        transaction.paid_at = timezone.now()
        transaction.paystack_reference = reference
        transaction.logistics_released = True  # Release logistics fee immediately
        transaction.save()
        
        # Set deadline (2 days + 1 day grace)
        transaction.set_deadline()
        
        # Send confirmation code via email
        send_confirmation_code_email(transaction)
        
        messages.success(request, 'Payment successful! Check your email for the confirmation code.')
        return redirect('payment_success', transaction_id=transaction.id)
    else:
        messages.error(request, f"Payment verification failed: {result['message']}")
        return redirect('home')

def payment_success(request, transaction_id):
    """Payment success page"""
    transaction = get_object_or_404(EscrowTransaction, id=transaction_id)
    return render(request, 'escrow/payment_success.html', {'transaction': transaction})

def confirm_delivery(request, transaction_id):
    """Buyer confirms delivery with code"""
    transaction = get_object_or_404(EscrowTransaction, id=transaction_id)
    
    if transaction.status not in ['paid']:
        messages.info(request, 'This transaction cannot be confirmed.')
        return redirect('home')
    
    if request.method == 'POST':
        entered_code = request.POST.get('confirmation_code')
        
        if entered_code == transaction.confirmation_code:
            transaction.status = 'confirmed'
            transaction.confirmed_at = timezone.now()
            transaction.product_released = True  # Release product payment to seller
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


    payment_url = request.build_absolute_uri(f'/pay/{transaction.id}/')

    return render(request, 'escrow/payment_link_detail.html', {
        'transaction': transaction,
        'payment_url': payment_url
    })

def SignUp(request):
    if request.method == 'GET':
        storage = get_messages(request)
        storage.used = True
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
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            has_error = True
            
        if len(password or '') < 6:  
            messages.error(request, 'Password must be at least 6 characters long.')
            has_error = True
      
        if not has_error:
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'User registered successfully!')
            return redirect('login')
    
    return render(request, 'escrow/signup.html')


def SignIn(request):
    if request.method == 'GET':
        storage = get_messages(request)
        storage.used = True
        return render(request, 'escrow/login.html')
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            authenticated_user = authenticate(request, username=user.username, password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)
                messages.success(request, 'Logged in successfully!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid email or password.')
        except User.DoesNotExist:
            user = None
            messages.error(request, 'Invalid email or password.')

    return render(request, 'escrow/login.html')

@login_required
def SignOut(request):
    """Logout user"""
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

@login_required
def seller_dashboard(request):
    """Simple seller dashboard showing all transactions"""
    try:
        seller = Seller.objects.get(user=request.user)
        transactions = EscrowTransaction.objects.filter(seller=seller).order_by('-created_at')
        
        context = {
            'seller': seller,
            'transactions': transactions,
        }
        return render(request, 'escrow/seller_dashboard.html', context)
    except Seller.DoesNotExist:
        messages.info(request, 'Please create your first payment link to set up your seller account.')
        return redirect('create_payment_link')