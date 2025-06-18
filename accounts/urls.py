from django.urls import path
from .views import UserRegistrationView, LogoutView, UserLoginView, OTPVerificationView,ManageProfileView,UserProfileView,NotificationListView,mark_notification_as_read



app_name = 'accounts'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_registration'),
    path('login/', UserLoginView.as_view(), name='user_login'),  # Make sure this line exists
    path('logout/', LogoutView.as_view(), name='user_logout'),
    path('verify_otp/<int:user_id>/', OTPVerificationView.as_view(), name='verify_otp'),
   # path('accounts/profile/manage/',ManageProfileView.as_view(),name='manage_profile'),

    path('profile/', UserProfileView.as_view(), name='profile'),
    path('manage/', ManageProfileView.as_view(), name='manage_profile'),  # Ensure this line exists
    # Other patterns...
    
    path('notifications/', NotificationListView.as_view(), name='notification_list'),
    path('notifications/mark_read/<int:notification_id>/', mark_notification_as_read, name='mark_notification_as_read'),

]

# In accounts/urls.py (or wherever your URL patterns are defined