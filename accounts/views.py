from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import TemplateView, RedirectView
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from .forms import UserRegistrationForm, UserAddressForm, OTPVerificationForm,UserProfileForm 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from .forms import UserProfileForm
from .models import User  # Import your custom user model

from django.shortcuts import render, redirect
from django.views import View
from .forms import UserProfileForm  # Import your UserProfileForm
from django.contrib import messages

from django.views.generic import ListView
from .models import Notification
from django.shortcuts import get_object_or_404, redirect
from .models import Notification
User = get_user_model()
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.mail import send_mail
from .forms import UserRegistrationForm, UserAddressForm, AuthenticationForm
from .models import User
from django.db import models

class UserRegistrationView(TemplateView):
    template_name = 'accounts/user_registration.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('transactions:transaction_report')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        registration_form = UserRegistrationForm(request.POST)
        address_form = UserAddressForm(request.POST)

        if registration_form.is_valid() and address_form.is_valid():
            user = registration_form.save()
            address = address_form.save(commit=False)
            address.user = user
            address.save()

            user.generate_otp()
            user.save()

            
            try:
                    send_mail(
                       
                        '               Rover Welcomes you!!',
                        

                        'Dear Customer,\n'

                        '\nCongratulations! We are thrilled to have you join our community.\n'
                        ' \n'

                        'Your registration was successful, and you can now explore all the exciting features we offer. Here are a few things you might want to check out:'
                        'As a registered user, you will receive the latest updates, offers, and news from ROVER. We encourage you to take advantage of all the resources available to you.\n'

                        '\nThank you for choosing rover. We look forward to serving you!\n'

                        '\n'

                        'Best regards,\n'
                        'Rover Team\n'
    

                        

                    #    f'Your OTP code is: {user.otp}',
                        'authenticatorforbankproject@gmail.com',  # Replace with your email
                        [user.email],
                        fail_silently=False,
                )




                
                    messages.success(request, "Registration successful!")
                    return redirect('accounts:user_login', user_id=user.id)
            except Exception:
            #    messages.error(request, "There was an error sending the OTP email. Please try again.")
                return redirect('accounts:user_login')

        return self.render_to_response(
            self.get_context_data(
                registration_form=registration_form,
                address_form=address_form
            )
        )

    def get_context_data(self, **kwargs):
        kwargs.setdefault('registration_form', UserRegistrationForm())
        kwargs.setdefault('address_form', UserAddressForm())
        return super().get_context_data(**kwargs)


class UserLoginView(TemplateView):
    template_name = 'accounts/user_login.html'

    def get(self, request, *args, **kwargs):
        form = AuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            identifier = form.cleaned_data.get('username')  # This can be either email or username
            password = form.cleaned_data.get('password')

            # Custom authentication to support login with either email or username
            user = User.objects.filter(models.Q(username=identifier) | models.Q(email=identifier)).first()
            if user and user.check_password(password):
                user.generate_otp()
                user.save()
                try:
                    send_mail(
                       
                        '               Rover Welcomes you!!',
                        

                        'Dear Customer,\n'

                       

                        '\nThank you for choosing rover. We look forward to serving you!\n'

                        '\n'

                        'Best regards,\n'
                        'Rover Team\n'
    

                        

                        f'Your OTP code is: {user.otp}',
                        'authenticatorforbankproject@gmail.com',  # Replace with your email
                        [user.email],
                        fail_silently=False,
                )

                
                    messages.success(request, "To Login successfully! An OTP has been sent to your email.")
                    return redirect('accounts:verify_otp', user_id=user.id)
                except Exception as e:
                  messages.error(request, f"There was an error sending the OTP email: {e}")
                  print("EMAIL ERROR:", e)
                  return redirect('accounts:user_login')

            else:
                messages.error(request, "Invalid email/username or password.")
        
        return render(request, self.template_name, {'form': form})


class OTPVerificationView(TemplateView):
    template_name = 'accounts/verify_otp.html'

    def get(self, request, *args, **kwargs):
        user_id = kwargs['user_id']
        return self.render_to_response({'user_id': user_id})

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs['user_id'])
        entered_otp = request.POST.get('otp')

        if user.is_otp_valid(entered_otp):
            user.clear_otp()
            login(request, user)
            messages.success(request, "You are now logged in!")
            return redirect('dashboard')  # Ensure 'dashboard' URL is defined
        else:
            messages.error(request, "Invalid or expired OTP. Please try again.")
            return self.render_to_response({'user_id': user.id, 'otp_error': True})


class LogoutView(RedirectView):
    url = '/'  # Adjust to your desired logout redirect URL

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "You have been logged out.")
        return super().get(request, *args, **kwargs)
 # Ensure this form is created


class ManageProfileView(View):
    def get(self, request):
        form = UserProfileForm(instance=request.user)
        return render(request, 'accounts/manage_profile.html', {'form': form})

    def post(self, request):
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            # Check if a new password is provided
            new_password = form.cleaned_data.get("new_password")
            if new_password:
                # Set the new password and save the user
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, "Profile updated successfully!")
            else:
                form.save()  # Only save other fields if no password change

            return redirect('dashboard')  # Redirect to home after successful update
        return render(request, 'accounts/manage_profile.html', {'form': form})


class UserProfileView(TemplateView):
    template_name = 'accounts/user_profile.html'  # Create this template to show user profile details


class NotificationListView(ListView):
    model = Notification
    template_name = 'accounts/notification_list.html'  # Adjust the template path as needed
    context_object_name = 'notifications'

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-timestamp')


from django.shortcuts import get_object_or_404, redirect
from .models import Notification

def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()  # Mark the notification as read
    return redirect('accounts:notification_list')  # Include the namespace



