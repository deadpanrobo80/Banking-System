from django.urls import path
from . import views
from .views import DepositMoneyView, WithdrawMoneyView, TransactionRepostView, TransferFundsView, TransferSuccessView,DashboardView,TransactiondownloadView,TransactionView
app_name = 'transactions'

urlpatterns = [
    path("deposit/", DepositMoneyView.as_view(), name="deposit_money"),
    path("report/", TransactionRepostView.as_view(), name="transaction_report"),  # Corrected here
    path("withdraw/", WithdrawMoneyView.as_view(), name="withdraw_money"),
    path("transfer/", TransferFundsView.as_view(), name="transfer_funds"),

    path('success/', TransferSuccessView.as_view(), name='success'),  # Renamed for clarity
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('transaction/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('api/account/balance/', views.get_account_balance, name='get_account_balance'),
    path('transaction/download/', TransactiondownloadView.as_view(), name='transaction_download'),
     path('transactions/reverse/<int:transaction_id>/', TransactionView.as_view(), name='reverse_transaction'), 
     
      

    

    # urls.py



]
