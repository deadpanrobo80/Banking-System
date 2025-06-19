from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView
from transactions.constants import DEPOSIT, WITHDRAWAL, TRANSFER
from transactions.forms import DepositForm, TransactionDateRangeForm, WithdrawForm, TransferForm
from transactions.models import Transaction
from accounts.models import UserBankAccount
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.views import View
from django.shortcuts import redirect 
from django.urls import reverse

class TransactionRepostView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    form_data = {}

    def get(self, request, *args, **kwargs):
        form = TransactionDateRangeForm(request.GET or None)
        if form.is_valid():
            self.form_data = form.cleaned_data
        
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )
        daterange = self.form_data.get("daterange")
        if daterange:
            queryset = queryset.filter(timestamp__date__range=daterange)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account,
            'form': TransactionDateRangeForm(self.request.GET or None),
            'download_url': reverse('transactions:transaction_download')
            
            
        })
        return context
    

class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transactions:transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })
        return context


class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit Money to Your Account'

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account

        if not account.initial_deposit_date:
            now = timezone.now()
            # Set initial deposit date and interest start date without using account_type
            account.initial_deposit_date = now
            account.interest_start_date = now + relativedelta(months=1)  # Just an example, adjust as needed

        account.balance += amount
        account.save(update_fields=['initial_deposit_date', 'balance', 'interest_start_date'])

        messages.success(self.request, f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully')
        return super().form_valid(form)


class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Money from Your Account'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account

        account.balance -= amount
        account.save(update_fields=['balance'])

        messages.success(self.request, f'Successfully withdrawn {"{:,.2f}".format(float(amount))}$ from your account')
        return super().form_valid(form)


class TransferFundsView(View):
    template_name = 'transactions/transfer_funds.html'

    def get(self, request, *args, **kwargs):
        account = UserBankAccount.objects.get(user=request.user)
        form = TransferForm(account=account)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        account = UserBankAccount.objects.get(user=request.user)
        form = TransferForm(request.POST, account=account)

        if form.is_valid():
            recipient_account = UserBankAccount.objects.get(account_no=form.cleaned_data['recipient_account_no'])
            amount = form.cleaned_data['amount']

            if account.balance < amount:
                messages.error(request, "Insufficient funds for this transfer.")
                return render(request, self.template_name, {'form': form})

            account.balance -= amount
            account.save()

            recipient_account.balance += amount
            recipient_account.save()

            Transaction.objects.create(
                account=account,
                amount=amount,
                balance_after_transaction=account.balance,
                transaction_type=TRANSFER
            )

            Transaction.objects.create(
                account=recipient_account,
                amount=amount,
                balance_after_transaction=recipient_account.balance,
                transaction_type=TRANSFER
            )

            messages.success(request, f'Successfully transferred {"{:,.2f}".format(float(amount))}$ to account {recipient_account.account_no}.')
            return redirect('dashboard')

        return render(request, self.template_name, {'form': form})


class TransferSuccessView(TemplateView):
    template_name = 'transactions/success.html'
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'transactions/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Assuming your CustomUser model has these fields
        context['first_name'] = user.first_name
        context['last_name'] = user.last_name
        context['email'] = user.email
        context['account_number'] = user.account.account_no  # Adjust if needed based on your model

        return context
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def get_account_balance(request):
    user = request.user  # Get the logged-in user
    account = user.account if hasattr(user, 'account') else None  # Check if the user has an account

    if account:
        balance = account.balance  # Fetch the balance
    else:
        balance = 0.00  # Default balance if no account exists

    return JsonResponse({'balance': float(balance)})  # Return the balance as JSON
import csv
from django.http import HttpResponse
from django.views import View
from .models import Transaction  # Assuming you have a Transaction model

import csv
from django.http import HttpResponse
from django.views import View
from .models import Transaction  # Assuming you have a Transaction model

import csv
from django.http import HttpResponse
from django.views import View
from .models import Transaction  # Make sure to import the Transaction model

class TransactiondownloadView(View):
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

        writer = csv.writer(response)
        writer.writerow(['Transaction ID', 'Account Number', 'Amount', 'Transaction Type', 'Date', 'Balance After Transaction'])

        # Fetch transactions for the logged-in user
        transactions = Transaction.objects.filter(account__user=request.user)

        for transaction in transactions:
            writer.writerow([
                transaction.id,
                transaction.account.account_no,
                transaction.amount,
                transaction.get_transaction_type_display(),
                transaction.timestamp,
                transaction.balance_after_transaction,
            ])

        return response
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.mail import send_mail

def report_fraud(request, transaction_id):
    if request.method == 'POST':
        # Notify admin about the reported fraud
        send_mail(
            'Fraud Reported',
            f"Transaction ID {transaction_id} has been reported as fraudulent.",
            'from@example.com',
            ['yogasrilella9093@gmail.com'],  # Replace with admin email
            fail_silently=False,
        )
        # Optionally redirect to a thank you page or confirmation
        return HttpResponseRedirect('/thank-you/')

    # Render a confirmation page or form to confirm fraud
    return render(request, 'report_fraud.html', {'transaction_id': transaction_id})
# views.py
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.core.mail import send_mail
from .models import Transaction

class TransactionView(View):
    def post(self, request, transaction_id):
        transaction = get_object_or_404(Transaction, id=transaction_id)
        
        if not transaction.flagged:
            transaction.flag()  # Flag the transaction
            
            # Send email notification to admin
            send_mail(
                'Transaction Flagged',
                f"Transaction ID {transaction_id} has been flagged by a user.",
                'yogasrilella9093@gmail.com',  # Replace with your email
                ['yogasrilella9093@gmail.com'],  # Replace with admin email
                fail_silently=False,
            )

            messages.success(request, "Transaction flagged successfully. The admin will be notified.")
        else:
            messages.warning(request, "Transaction is already flagged.")

        return redirect('dashboard')  # Redirect to the dashboard after flagging

