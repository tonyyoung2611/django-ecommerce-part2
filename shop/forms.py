
"""Forms used for registration, reviews, stores, and products.

This module defines the forms that collect and validate
user input throughout the eCommerce application.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Product, Review, Store


class RegistrationForm(UserCreationForm):
    """Collect account details and the user's selected role."""

    # Require an email address during registration.
    email = forms.EmailField(required=True)

    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('vendor', 'Vendor'),
    ]

    # Allow new users to register as buyers or vendors.
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        """Define the user model and registration form fields."""

        model = User
        fields = [
            'username',
            'email',
            'role',
            'password1',
            'password2',
        ]


class ReviewForm(forms.ModelForm):
    """Collect a product rating and written customer review."""

    # Restrict ratings to values between 1 and 5.
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        label="Rating (1-5)"
    )

    class Meta:
        """Define the review model and editable fields."""

        model = Review
        fields = ['rating', 'comment']


class StoreForm(forms.ModelForm):
    """Collect information when creating or editing a store."""

    class Meta:
        """Define the store model and editable fields."""

        model = Store
        fields = ['name', 'description']


class ProductForm(forms.ModelForm):
    """Collect product details and restrict store selection by owner."""

    class Meta:
        """Define the product model and editable fields."""

        model = Product
        fields = [
            'store',
            'name',
            'description',
            'price',
            'stock',
        ]

    def __init__(self, *args, **kwargs):
        """Limit available stores to those owned by the current user."""

        # Retrieve the current user passed in by the product view.
        user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        if user is not None:
            # Vendors can only select stores they own.
            self.fields['store'].queryset = Store.objects.filter(
                owner=user
            )
        else:
            # Without a user, no stores can be selected.
            self.fields['store'].queryset = Store.objects.none()
