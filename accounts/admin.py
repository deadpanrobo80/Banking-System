from django.contrib import admin
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.db import transaction
from django.db import models
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

from .models import User, UserAddress, UserBankAccount


#admin.site.register(User)
admin.site.register(UserAddress)
admin.site.register(UserBankAccount)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active']
    search_fields = ['email', 'username']  # Enable searching by email and username

admin.site.register(User, CustomUserAdmin)
