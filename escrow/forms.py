from .models import EscrowTransaction, Seller
import random
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegForm(UserCreationForm):
    class Meta:
        model = User
        fields = "__all__"


class EscrowTransactionForm(forms.ModelForm):
    class Meta:
        model = EscrowTransaction
        fields = [
            'product_name', 'product_price', 'logistics_fee',
            'buyer_phone', 'buyer_email'
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'product_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'logistics_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'buyer_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'buyer_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
class SellerRegistrationForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['phone', 'bank_account']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
        }
class PaymentForm(forms.Form):
    
    confirmation_code = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Confirmation Code'})
    )
    def clean_confirmation_code(self):
        code = self.cleaned_data.get('confirmation_code')
        if not code.isdigit():
            raise forms.ValidationError("Confirmation code must be numeric.")
        return code