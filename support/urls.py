# urls.py
from django.urls import path
from .views import SubmitTicketView, TicketListView, TicketDetailView

app_name = 'support'

urlpatterns = [
    path('submit/', SubmitTicketView.as_view(), name='submit_ticket'),
    path('my-tickets/', TicketListView.as_view(), name='ticket_list'),
      path('ticket/<int:pk>/', TicketDetailView.as_view(), name='ticket_detail'),
]
