from django import forms
from .models import Loan, LoanCategory
from django.core.exceptions import ValidationError

class LoanRepaymentForm(forms.ModelForm):
    repayment_amount = forms.DecimalField(
        decimal_places=2,
        max_digits=12,
        label="Repayment Amount",
        min_value=0.01,  # Ensure the amount is positive
    )

    class Meta:
        model = Loan
        fields = []  # No need to include any fields since we're only using repayment_amount

    def __init__(self, *args, **kwargs):
        self.loan = kwargs.pop('loan', None)  # Pass the loan instance when initializing
        super().__init__(*args, **kwargs)
        if not self.loan:
            raise ValueError("A valid Loan instance must be provided to LoanRepaymentForm.")

    def clean_repayment_amount(self):
        repayment_amount = self.cleaned_data.get('repayment_amount')

        if repayment_amount <= 0:
            raise forms.ValidationError("Please enter an amount greater than zero.")
        
        # Check loan status and remaining balance
        if self.loan:
            if self.loan.status != 'approved':
                raise forms.ValidationError("Repayments are only allowed on approved loans.")
            if repayment_amount > self.loan.remaining_balance:
                raise forms.ValidationError(f"Repayment amount exceeds the remaining balance of {self.loan.remaining_balance:.2f}. Please enter a valid amount.")
        
        return repayment_amount

    def save(self, commit=True):
        """Override the save method to update the loan balance and status."""
        repayment_amount = self.cleaned_data['repayment_amount']
        
        # Deduct repayment amount from the loan's remaining balance
        self.loan.remaining_balance -= repayment_amount
        
        # Mark the loan as completed if the remaining balance is zero
        if self.loan.remaining_balance <= 0:
            self.loan.remaining_balance = 0  # Ensure no negative balance
            self.loan.status = 'completed'

        # Save changes to the loan
        if commit:
            self.loan.save()

        return self.loan


class LoanApplicationForm(forms.ModelForm):
    application_fee = forms.DecimalField(
        decimal_places=2,
        max_digits=12,
        initial=100.00,
        label="Application Fee",
        disabled=True  # Application fee is fixed and cannot be changed
    )

    category = forms.ModelChoiceField(
        queryset=LoanCategory.objects.all(),
        label="Loan Category",
        empty_label="Select a category",
        required=True  # Make category required
    )

    class Meta:
        model = Loan
        fields = ['amount', 'repayment_period_months', 'category']  # Include necessary fields

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        
        # Validate loan amount
        if amount is None:
            raise ValidationError("Loan amount is required.")
        if amount <= 0:
            raise ValidationError("Loan amount must be greater than zero.")
        
        return amount

    def clean_repayment_period_months(self):
        repayment_period_months = self.cleaned_data.get('repayment_period_months')
        
        # Validate repayment period
        if repayment_period_months is None:
            raise ValidationError("Repayment period is required.")
        if repayment_period_months <= 0:
            raise ValidationError("Repayment period must be greater than zero.")
        
        return repayment_period_months
