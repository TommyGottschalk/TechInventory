from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Request, Inventory


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserAddForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_superuser',
            'is_active',
            'password1',
            'password2',
        ]


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_superuser',
            'is_active',
        ]

class RequestEditForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = [
            'user',
            'inventory',
            'return_date',
            'actual_return_date',
            'charger_requested',
            'status',
        ]

class InventoryEditForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = [
            'product_model',
            'storage_size',
            'is_available',
        ]