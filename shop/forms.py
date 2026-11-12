
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review, Store, Product



class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('vendor', 'Vendor'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'role',
            'password1',
            'password2'
        ]


class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        label="Rating (1-5)"
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'description']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'store',
            'name',
            'description',
            'price',
            'stock'
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields['store'].queryset = Store.objects.filter(
                owner=user
            )
        else:
            self.fields['store'].queryset = Store.objects.none()
