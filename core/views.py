from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
#from accounts.models import Account  # Adjust import based on your structure
class HomeView(TemplateView):
    template_name = 'core/index.html'

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'transactions/dashboard.html'


class DepositView(LoginRequiredMixin, TemplateView):
    template_name = 'core/deposit.html'

class WithdrawView(LoginRequiredMixin, TemplateView):
    template_name = 'core/withdraw.html'

class TransferFundsView(LoginRequiredMixin, TemplateView):
    template_name = 'core/transfer_funds.html'

class ApplyLoanView(LoginRequiredMixin, TemplateView):
    template_name = 'core/apply_loan.html'

class LoanReportView(LoginRequiredMixin, TemplateView):
    template_name = 'core/loan_report.html'

