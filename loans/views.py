
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Loan
from .forms import LoanApplicationForm, LoanRepaymentForm
from accounts.models import Notification  # Assuming a Notification model exists

# Loan Application View
class LoanApplicationView(LoginRequiredMixin, View):
    def get(self, request):
        form = LoanApplicationForm()
        return render(request, 'loans/loan_application.html', {'form': form})

    def post(self, request):
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.account = request.user.account  # Ensure association with the user's account
            loan.save()
            
            # Send notification
            Notification.objects.create(
                user=loan.account.user,
                message=f"Your loan application for {loan.amount} is submitted."
            )
            return redirect('loans:loan_success')
        return render(request, 'loans/loan_application.html', {'form': form})

# Loan Report View
class LoanReportView(LoginRequiredMixin, View):
    def get(self, request):
        loans = Loan.objects.filter(account__user=request.user)
        return render(request, 'loans/loan_dasnboard.html', {'loans': loans})

# Loan Success View
class LoanSuccessView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'loans/loan_success.html')

# Loan Status View
class LoanStatusView(LoginRequiredMixin, View):
    def get(self, request):
        loans = Loan.objects.filter(account__user=request.user)
        return render(request, 'loans/loan_status.html', {'loans': loans})
import logging
logger = logging.getLogger(__name__)
# Loan Repayment View
import logging
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from .models import Loan, Notification  # Ensure you have the correct imports
from .forms import LoanRepaymentForm  # Ensure you have the correct imports

# Set up the logger
logger = logging.getLogger(__name__)
import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .models import Loan, Notification  # Ensure Notification model is imported
from .forms import LoanRepaymentForm  # Ensure your form is imported

logger = logging.getLogger(__name__)

import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .models import Loan
from .forms import LoanRepaymentForm

# Setting up a logger
logger = logging.getLogger(__name__)

class LoanRepaymentView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        logger.debug(f"Searching for loan with ID: {loan_id} and user: {request.user}")

        # Try to retrieve the loan object associated with the user
        loan = Loan.objects.filter(loan_id=loan_id, account__user=request.user).first()
        
        if not loan:
            logger.warning(f"No loan found for loan_id: {loan_id} and user: {request.user}")
            return render(request, 'loans/error.html', {'message': 'No Loan matches the given query.'})

        logger.debug(f"Loan found: {loan}. Preparing form.")
        form = LoanRepaymentForm(loan=loan)  # Pass the loan instance to the form
        return render(request, 'loans/loan_repayment.html', {'form': form, 'loan': loan})

    def post(self, request, loan_id):
        # Ensure the loan is fetched from the database
        loan = get_object_or_404(Loan, loan_id=loan_id, account__user=request.user)

        form = LoanRepaymentForm(request.POST, loan=loan)  # Pass the loan instance to the form
        if form.is_valid():
            repayment_amount = form.cleaned_data['repayment_amount']
            
            # Ensure repayment amount does not exceed the remaining balance
            if repayment_amount > loan.remaining_balance:
                form.add_error('repayment_amount', f"Repayment exceeds remaining balance of {loan.remaining_balance:.2f}.")
                return render(request, 'loans/loan_repayment.html', {'form': form, 'loan': loan})

            if repayment_amount <= 0:
                form.add_error('repayment_amount', "Repayment amount must be greater than zero.")
                return render(request, 'loans/loan_repayment.html', {'form': form, 'loan': loan})

            # Update the loan's remaining balance
            loan.remaining_balance -= repayment_amount
            
            # Check if the loan is completely paid off
            if loan.remaining_balance <= 0:
                loan.status = 'completed'  # Update status to completed
                loan.remaining_balance = 0  # Set to 0 to avoid negative balance

            loan.save()
            user_account = loan.account
            if user_account.balance < repayment_amount:
                        form.add_error(None, "Insufficient balance in the user's bank account.")
                        return render(request, 'loans/loan_repayment.html', {'form': form, 'loan': loan})

            else:         # Deduct the repayment from the user's bank account balance
                user_account.balance -= repayment_amount
                user_account.save() 
                Notification.objects.create(
                        user=loan.account.user,
                        message=f"Repayment of {repayment_amount} processed for your loan (ID: {loan_id})."
                    )
                logger.info(f"Repayment of {repayment_amount} processed for loan ID: {loan_id}. Remaining balance: {loan.remaining_balance:.2f}")

            # Redirect to a success page
                return redirect(reverse('loans:loan_dasnboard'))  # Ensure you have a loan_success view configured in your urls.py

        # Log form errors if the form is invalid
        logger.debug(f"Form errors: {form.errors}")
        return render(request, 'loans/loan_repayment.html', {'form': form, 'loan': loan})


# Loan Dashboard View
class LoanDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        loans = Loan.objects.filter(account__user=request.user)
        return render(request, 'loans/loan_dasnboard.html', {'loans': loans})

# Dashboard Redirect View
class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        loan = Loan.objects.filter(account__user=request.user).first()
        if loan:
            return redirect(reverse('loan_dasnoard', args=[loan.pk]))
        return redirect('home')  # Redirect to home if no loans found
