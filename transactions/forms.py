'''import datetime
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from accounts.models import UserBankAccount
from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'amount',
            'transaction_type'
        ]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()


class DepositForm(TransactionForm):
    def clean_amount(self):
        min_deposit_amount = settings.MINIMUM_DEPOSIT_AMOUNT
        amount = self.cleaned_data.get('amount')

        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount} $'
            )

        return amount


class WithdrawForm(TransactionForm):
    def clean_amount(self):
        account = self.account
        min_withdraw_amount = settings.MINIMUM_WITHDRAWAL_AMOUNT
        max_withdraw_amount = account.account_type.maximum_withdrawal_amount
        balance = account.balance

        amount = self.cleaned_data.get('amount')

        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at least {min_withdraw_amount} $'
            )

        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at most {max_withdraw_amount} $'
            )

        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance} $ in your account. '
                'You cannot withdraw more than your account balance.'
            )

        return amount


class TransactionDateRangeForm(forms.Form):
    daterange = forms.CharField(required=False)

    def clean_daterange(self):
        daterange = self.cleaned_data.get("daterange")
        print(daterange)

        try:
            daterange = daterange.split(' - ')
            print(daterange)
            if len(daterange) == 2:
                for date in daterange:
                    datetime.datetime.strptime(date, '%Y-%m-%d')
                return daterange
            else:
                raise forms.ValidationError("Please select a date range.")
        except (ValueError, AttributeError):
            raise forms.ValidationError("Invalid date range")

# In transactions/forms.py

class TransferForm(forms.Form):
    recipient_account_no = forms.CharField(required=True)
    amount = forms.DecimalField(max_digits=12, decimal_places=2)

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)
        super().__init__(*args, **kwargs)

    def clean_recipient_account_no(self):
        account_no = self.cleaned_data['recipient_account_no']
        try:
            UserBankAccount.objects.get(account_no=account_no)
        except UserBankAccount.DoesNotExist:
            raise ValidationError("The recipient account does not exist.")
        return account_no

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        if amount <= 0:
            raise ValidationError("Transfer amount must be positive.")
        if self.account is None:
            raise ValidationError("Account not found.")
        if amount > self.account.balance:
            raise ValidationError("Insufficient funds for this transfer.")

        return amount
'''
import datetime
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from accounts.models import UserBankAccount
from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type']

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save(commit=commit)


class DepositForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        min_deposit_amount = settings.MINIMUM_DEPOSIT_AMOUNT

        if amount < min_deposit_amount:
            raise ValidationError(f'You need to deposit at least {min_deposit_amount} $')
        return amount


class WithdrawForm(TransactionForm):
    def clean_amount(self):
        account = self.account
        amount = self.cleaned_data.get('amount')

        min_withdraw_amount = settings.MINIMUM_WITHDRAWAL_AMOUNT
    #    max_withdraw_amount = account.account_type.maximum_withdrawal_amount
        balance = account.balance

        if amount < min_withdraw_amount:
            raise ValidationError(f'You can withdraw at least {min_withdraw_amount} $')
    
        if amount > balance:
            raise ValidationError(f'You have {balance} $ in your account. You cannot withdraw more than your account balance.')

        return amount


class TransactionDateRangeForm(forms.Form):
    daterange = forms.CharField(required=False)

    def clean_daterange(self):
        daterange = self.cleaned_data.get("daterange")
        if not daterange:
            return None  # No date range provided

        try:
            start_date, end_date = daterange.split(' - ')
            datetime.datetime.strptime(start_date, '%Y-%m-%d')
            datetime.datetime.strptime(end_date, '%Y-%m-%d')
            return daterange
        except ValueError:
            raise ValidationError("Invalid date range format. Use YYYY-MM-DD - YYYY-MM-DD.")


class TransferForm(forms.Form):
    recipient_account_no = forms.CharField(required=True)
    amount = forms.DecimalField(max_digits=12, decimal_places=2)

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)
        super().__init__(*args, **kwargs)

    def clean_recipient_account_no(self):
        account_no = self.cleaned_data['recipient_account_no']
        if not UserBankAccount.objects.filter(account_no=account_no).exists():
            raise ValidationError("The recipient account does not exist.")
        return account_no

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        if amount <= 0:
            raise ValidationError("Transfer amount must be positive.")
        if self.account is None:
            raise ValidationError("Account not found.")
        if amount > self.account.balance:
            raise ValidationError("Insufficient funds for this transfer.")

        return amount
