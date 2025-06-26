from fpdf import FPDF

# Creating a PDF document
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Setting Title
pdf.set_font("Arial", 'B', 16)
pdf.cell(200, 10, txt="Seamless Bank System - Implementation Details", ln=True, align="C")
pdf.ln(10)

# Setting Subtitle
pdf.set_font("Arial", 'B', 12)
pdf.cell(200, 10, txt="Account Module Implementation", ln=True)
pdf.set_font("Arial", size=12)
pdf.multi_cell(0, 10, """
The Account Module allows users to create and manage personal banking accounts. Users can 
deposit, withdraw, and view their account balance and transaction history.

1. Models: Account and Transaction Models
The Account model stores information about the account type, balance, and links to the user. 
The Transaction model records deposit and withdrawal activities.

Code for models (models.py):
    from django.db import models
    from django.contrib.auth.models import User  # User authentication
    class Account(models.Model):
        user = models.OneToOneField(User, on_delete=models.CASCADE)
        balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
        account_type = models.CharField(max_length=50, choices=[('Savings', 'Savings'), ('Checking', 'Checking')], default='Savings')

    class Transaction(models.Model):
        account = models.ForeignKey(Account, on_delete=models.CASCADE)
        amount = models.DecimalField(max_digits=12, decimal_places=2)
        transaction_type = models.CharField(max_length=50, choices=[('Deposit', 'Deposit'), ('Withdrawal', 'Withdrawal')])
        timestamp = models.DateTimeField(auto_now_add=True)

2. Forms and Views
Forms to handle deposit and withdrawal operations, and views for displaying account information and handling POST requests.

    from django import forms
    class DepositForm(forms.Form):
        amount = forms.DecimalField(max_digits=10, decimal_places=2)

    from django.shortcuts import render, redirect
    from .models import Account, Transaction
    from django.contrib.auth.decorators import login_required
    from django.contrib import messages

    @login_required
    def account_overview(request):
        account = Account.objects.get(user=request.user)
        transactions = Transaction.objects.filter(account=account).order_by('-timestamp')
        return render(request, 'account_overview.html', {'account': account, 'transactions': transactions})

    @login_required
    def deposit(request):
        if request.method == 'POST':
            amount = float(request.POST.get('amount'))
            account = Account.objects.get(user=request.user)
            account.deposit(amount)
            Transaction.objects.create(account=account, amount=amount, transaction_type='Deposit')
            messages.success(request, 'Deposit successful')
            return redirect('account_overview')

    @login_required
    def withdraw(request):
        if request.method == 'POST':
            amount = float(request.POST.get('amount'))
            account = Account.objects.get(user=request.user)
            try:
                account.withdraw(amount)
                Transaction.objects.create(account=account, amount=amount, transaction_type='Withdrawal')
                messages.success(request, 'Withdrawal successful')
            except ValueError as e:
                messages.error(request, str(e))
            return redirect('account_overview')
""")

pdf.ln(5)

# Loan Module
pdf.set_font("Arial", 'B', 12)
pdf.cell(200, 10, txt="Loan Module Implementation", ln=True)
pdf.set_font("Arial", size=12)
pdf.multi_cell(0, 10, """
The Loan Module allows users to apply for loans, view loan statuses, and make repayments. 

1. Models: Loan and Repayment Models
The Loan model tracks loan details like the amount, tenure, interest rate, and approval status. 
The Repayment model records each repayment made by the user.

Code for models (models.py):
    class Loan(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE)
        amount = models.DecimalField(max_digits=12, decimal_places=2)
        interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
        tenure = models.IntegerField(help_text="In months")
        approved = models.BooleanField(default=False)
        date_applied = models.DateTimeField(auto_now_add=True)

    class Repayment(models.Model):
        loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
        amount = models.DecimalField(max_digits=12, decimal_places=2)
        repayment_date = models.DateTimeField(auto_now_add=True)

2. Views
The views handle loan application, approval, repayment, and loan status.

    from django.shortcuts import render, redirect
    from .models import Loan, Repayment
    from django.contrib.auth.decorators import login_required
    from django.contrib import messages

    @login_required
    def apply_for_loan(request):
        if request.method == 'POST':
            amount = float(request.POST.get('amount'))
            tenure = int(request.POST.get('tenure'))
            interest_rate = 5  # Static rate for simplicity
            loan = Loan.objects.create(user=request.user, amount=amount, interest_rate=interest_rate, tenure=tenure)
            messages.success(request, 'Loan application submitted successfully')
            return redirect('loan_application_status')
        return render(request, 'apply_for_loan.html')

    @login_required
    def loan_application_status(request):
        loan = Loan.objects.filter(user=request.user).last()  # Get latest loan
        return render(request, 'loan_application_status.html', {'loan': loan})

    @login_required
    def make_repayment(request, loan_id):
        loan = Loan.objects.get(id=loan_id)
        if request.method == 'POST':
            amount = float(request.POST.get('amount'))
            if amount <= loan.amount:
                Repayment.objects.create(loan=loan, amount=amount)
                loan.amount -= amount  # Update the loan amount
                loan.save()
                messages.success(request, 'Repayment successful')
            else:
                messages.error(request, 'Repayment amount exceeds loan balance')
            return redirect('loan_application_status')
""")

pdf.ln(5)

# Banking System Module
pdf.set_font("Arial", 'B', 12)
pdf.cell(200, 10, txt="Banking System (Main) Module Implementation", ln=True)
pdf.set_font("Arial", size=12)
pdf.multi_cell(0, 10, """
The Banking System Module serves as the main interface for users to manage accounts, loans, 
and perform other banking-related activities.

1. Dashboard View
The dashboard serves as a central location where users can view their accounts and loan information.

Code for views (views.py):
    @login_required
    def dashboard(request):
        accounts = Account.objects.filter(user=request.user)
        loans = Loan.objects.filter(user=request.user)
        return render(request, 'dashboard.html', {'accounts': accounts, 'loans': loans})

2. Integration of All Modules
The main banking system integrates the Account and Loan modules, offering a seamless user experience. 
Users can manage their accounts, apply for loans, and track financial activities in one place.
""")

# Outputting PDF
file_path = "\Users\bzwak\Downloads\"Seamless_Bank_System_Implementation.pdf"
pdf.output(file_path)

file_path
