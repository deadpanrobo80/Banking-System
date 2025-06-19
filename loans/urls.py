from django.urls import path
from .views import LoanApplicationView,  LoanReportView,LoanSuccessView,LoanStatusView,LoanStatusView,LoanRepaymentView

app_name = 'loans'

urlpatterns = [
    path('apply/', LoanApplicationView.as_view(), name='loan_application'),
 
    path('report/', LoanReportView.as_view(), name='loan_dasnboard'),
    path('loan/', LoanSuccessView.as_view(), name='loan_success'),
    path('loan/status/', LoanStatusView.as_view(), name='loan_status'),
   
    path('repay/<uuid:loan_id>/', LoanRepaymentView.as_view(), name='loan_repayment'),

 
    

]
