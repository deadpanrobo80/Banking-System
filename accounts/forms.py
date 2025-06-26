from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db import transaction

from .models import User, UserBankAccount, UserAddress
from .constants import GENDER_CHOICE
from django import forms
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.utils.translation import gettext_lazy as _

class AuthenticationForm(BaseAuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

    class Meta:
        model = User  # Assuming you're using a custom User model
        fields = ['username', 'password']

class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = [
            'street_address',
            'city',
            'postal_code',
            'country'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        label="Enter OTP",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter OTP'})
    )

    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        if len(otp) != 6:
            raise forms.ValidationError("OTP must be 6 digits.")
        return otp

class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=150, required=True, help_text='Required. 150 characters or fewer.')
    gender = forms.ChoiceField(choices=GENDER_CHOICE)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'autofocus': 'on'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': 'off'}))

    class Meta:
        model = User
        fields = [
            'username',      # Added username to fields
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            'gender',
            'birth_date',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 '
                    'rounded py-3 px-4 leading-tight '
                    'focus:outline-none focus:bg-white '
                    'focus:border-gray-500'
                )
            })

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()

        gender = self.cleaned_data.get('gender')
        birth_date = self.cleaned_data.get('birth_date')

        UserBankAccount.objects.create(
            user=user,
            gender=gender,
            birth_date=birth_date,
            account_no=(
                user.id +
                settings.ACCOUNT_NUMBER_START_FROM
            )
        )
        return user

class UserProfileForm(UserChangeForm):
    new_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label="Confirm New Password"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']  # Added username to fields

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'
            })

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and new_password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data
